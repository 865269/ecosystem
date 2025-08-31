from mesa.visualization.modules import CanvasGrid, TextElement
from mesa.visualization.UserParam import Slider
from mesa.visualization.ModularVisualization import ModularServer
from ecosystem import Ecosystem, Rabbit, Fox, Grass

def agent_portrayal(agent):
    if isinstance(agent, Rabbit):
        return {"Shape": "circle", "Color": "blue", "r": 0.5, "Layer": 0}
    elif isinstance(agent, Fox):
        return {"Shape": "circle", "Color": "red", "r": 0.7, "Layer": 0}
    elif isinstance(agent, Grass):
        return {"Shape": "circle", "Color": "green", "r": 0.3, "Layer": 0}
    return {}

class PopulationCount(TextElement):
    def render(self, model):
        rabbit_count = sum(isinstance(a, Rabbit) for a in model.schedule.agents)
        fox_count = sum(isinstance(a, Fox) for a in model.schedule.agents)
        # TODO add fully grown grass count
        return f"Rabbit count: {rabbit_count} | Fox count: {fox_count}"


# Create a 20x20 grid with 400px canvas
grid = CanvasGrid(agent_portrayal, 20, 20, 400, 400)

population_count_element = PopulationCount()

server = ModularServer(
    Ecosystem,
    [population_count_element, grid],
    "Ecosystem Simulation",
    {
        "width": 20,
        "height": 20,
        "N_rabbits": Slider("Number of Rabbits", 50, 10, 200, 10),
        "N_foxes": Slider("Number of Foxes", 5, 1, 50, 1)
    }
)

server.port = 8521
server.launch()