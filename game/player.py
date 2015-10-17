import networkx as nx
import random
import operator
from base_player import BasePlayer
from settings import *

class Player(BasePlayer):
    """
    You will implement this class for the competition. DO NOT change the class
    name or the base class.
    """

    # You can set up static state here
    has_built_station = False

    def __init__(self, state):
        """
        Initializes your Player. You can set up persistent state, do analysis
        on the input graph, engage in whatever pre-computation you need. This
        function must take less than Settings.INIT_TIMEOUT seconds.
        --- Parameters ---
        state : State
            The initial state of the game. See state.py for more information.
        """

        return

    # Checks if we can use a given path
    def path_is_valid(self, state, path):
        graph = state.get_graph()
        for i in range(0, len(path) - 1):
            if graph.edge[path[i]][path[i + 1]]['in_use']:
                return False
        return True

    # Finds the time value of the node
    def node_worth(self, order, path_length):
        return order.money - (path_length * DECAY_FACTOR)


    def step(self, state):
        """
        Determine actions based on the current state of the city. Called every
        time step. This function must take less than Settings.STEP_TIMEOUT
        seconds.
        --- Parameters ---
        state : State
            The state of the game. See state.py for more information.
        --- Returns ---
        commands : dict list
            Each command should be generated via self.send_command or
            self.build_command. The commands are evaluated in order.
        """

        # We have implemented a naive bot for you that builds a single station
        # and tries to find the shortest path from it to first pending order.
        # We recommend making it a bit smarter ;-)

        #print(state.money)

        graph = state.get_graph()
        #station = graph.nodes()[0]



        commands = []
        if not self.has_built_station:
            centrals = nx.closeness_centrality(graph)
            sorted_centrals = sorted(centrals.items(), key=operator.itemgetter(1))
            self.station = sorted_centrals[-1][0]
            commands.append(self.build_command(self.station))
            self.has_built_station = True

        # Copy graph and remove taken nodes
        free_graph = state.get_graph().copy()
        for active_order in state.get_active_orders():
            active_order_nodes = active_order[1]
            for i in range(0, len(active_order_nodes) - 1):
                free_graph.remove_edge(active_order_nodes[i], active_order_nodes[i + 1])

        pending_orders = state.get_pending_orders()
        print(state.get_active_orders())

        if len(pending_orders) != 0:
            def sorter(x): x.money - (len(nx.shortest_path(graph, self.station, x.get_node())) * DECAY_FACTOR)
            sorted_orders = sorted(pending_orders, key=sorter)

            # Go through orders from most to least value
            for order in reversed(sorted_orders):
                try:
                    path = nx.shortest_path(free_graph, self.station, order.get_node())
                    # Remove edge from free graph if path is being used
                    for i in range(0, len(path) - 1):
                        free_graph.remove_edge(path[i], path[i + 1])
                    commands.append(self.send_command(order, path))
                except nx.NetworkXNoPath:
                    print("Order is unreachable right now.")

        return commands
