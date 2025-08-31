from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

class Animal(Agent):
    def __init__(self, unique_id, model, energy):
        super().__init__(unique_id, model)
        self.energy = energy

    def remove(self):
        self.model.grid.remove_agent(self)
        self.model.schedule.remove(self)
    
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

        dx, dy = self.random.choice([-1, 0, 1]), self.random.choice([-1, 0, 1])
        new_pos = ((x + dx) % self.model.grid.width,
                   (y + dy) % self.model.grid.height)

        self.model.grid.move_agent(self, new_pos)


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

                self.model.grid.remove_agent(agent)
                self.model.schedule.remove(agent)
                break


class Ecosystem(Model):
    def __init__(self, width=20, height=20, N_rabbits=50, N_foxes=5, animal_energy=100):
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

    def step(self):
        self.schedule.step()
