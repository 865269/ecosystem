from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

class Animal(Agent):
    def __init__(self, unique_id, model, energy):
        super().__init__(unique_id, model)
        self.energy = energy

    def remove(self):
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)

    def reproduce(self):
        occupants = self.model.grid.get_cell_list_contents([self.pos])
        for agent in occupants:
            if isinstance(agent, self.__class__):
                # 40% chance to reproduce
                if self.random.random() < 0.4 and agent.energy >= 50:
                    self.energy /= 2
                    agent.energy /= 2
                    new_id = max([a.unique_id for a in self.model.schedule.agents]) + 1
                    new_agent = self.__class__(new_id, self.model, 100)
                    self.model.schedule.add(new_agent)
                    self.model.grid.place_agent(new_agent, self.pos)
                    break

    def step(self):
        self.move()

        self.energy -= 1

        if self.energy < 0:
            self.remove()
        elif self.energy >= 50:
            self.reproduce()


class Rabbit(Animal):

    def move(self):
        x, y = self.pos

        neighbor_positions = self.model.grid.get_neighborhood((x, y), moore=True, include_center=False)

        safe_positions = []
        for pos in neighbor_positions:
            if not any(isinstance(agent, Fox) for agent in self.model.grid.get_cell_list_contents([pos])):
                safe_positions.append(pos)

        if len(safe_positions) == 0:
            # If no safe positions, stay in place
            return

        positions_with_grass = []
        for pos in safe_positions:
            if any(isinstance(agent, Grass) and agent.fully_grown for agent in self.model.grid.get_cell_list_contents([pos])):
                positions_with_grass.append(pos)

        new_pos = self.pos
        if len(positions_with_grass) > 0 and self.energy < 30:
            new_pos = self.random.choice(positions_with_grass)
        else:
            dx, dy = self.random.choice([-1, 0, 1]), self.random.choice([-1, 0, 1])
            new_pos = ((x + dx) % self.model.grid.width,
                       (y + dy) % self.model.grid.height)

        self.model.grid.move_agent(self, new_pos)

    def feed(self):
        occupants = self.model.grid.get_cell_list_contents([self.pos])
        for agent in occupants:
            if isinstance(agent, Grass):
                if agent.fully_grown:
                    self.energy += 20
                    if self.energy > 100:
                        self.energy = 100
                    agent.be_eaten()
                break


class Fox(Animal):

    def move(self):
        x, y = self.pos

        dx, dy = self.random.choice([-1, 0, 1]), self.random.choice([-1, 0, 1])
        new_pos = ((x + dx) % self.model.grid.width,
                   (y + dy) % self.model.grid.height)

        self.model.grid.move_agent(self, new_pos)

    def feed(self):
        occupants = self.model.grid.get_cell_list_contents([self.pos])
        for agent in occupants:
            if isinstance(agent, Rabbit):
                self.energy += 20
                if self.energy > 100:
                    self.energy = 100
                agent.remove()
                break


class Grass(Agent):
    def __init__(self, unique_id, model, fully_grown=True, regrow_time=10):
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.regrow_time = regrow_time
        self.timer = 0

    def step(self):
        if not self.fully_grown:
            self.timer += 1
            if self.timer >= self.regrow_time:
                self.fully_grown = True
                self.timer = 0

    def be_eaten(self):
        self.fully_grown = False
        self.timer = 0


class Ecosystem(Model):
    def __init__(self, width=20, height=20, N_rabbits=50, N_foxes=5, N_grass=50, animal_energy=100):
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)

        for i in range(N_rabbits):
            rabbit = Rabbit(i, self, animal_energy)
            self.schedule.add(rabbit)
            x, y = self.random.randrange(width), self.random.randrange(height)
            self.grid.place_agent(rabbit, (x, y))

        for i in range(N_foxes):
            fox = Fox(N_rabbits + i, self, animal_energy)
            self.schedule.add(fox)
            x, y = self.random.randrange(width), self.random.randrange(height)
            self.grid.place_agent(fox, (x, y))

        # TODO make sure grass doesn't overlap with other grass
        for i in range(N_grass):
            grass = Grass(N_rabbits + N_foxes + i, self)
            self.schedule.add(grass)
            x, y = self.random.randrange(width), self.random.randrange(height)
            self.grid.place_agent(grass, (x, y))

    def step(self):
        self.schedule.step()
