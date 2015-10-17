import operator
import networkx as nx
import random
from base_player import BasePlayer
from settings import *
import math

class Player(BasePlayer):
    """
    You will implement this class for the competition. DO NOT change the class
    name or the base class.
    """

    def __init__(self, state):
        """
        Initializes your Player. You can set up persistent state, do analysis
        on the input graph, engage in whatever pre-computation you need. This
        function must take less than Settings.INIT_TIMEOUT seconds.
        --- Parameters ---
        state : State
            The initial state of the game. See state.py for more information.
        """
        self.built_station = False
        centrals = nx.closeness_centrality(state.get_graph())
        sorted_centrals = sorted(centrals.items(), key=operator.itemgetter(1))
        self.station = sorted_centrals[-1][0]
        self.old_pending_orders = []

    # Checks if we can use a given path
    def path_is_valid(self, state, path):
        graph = state.get_graph()
        for i in range(0, len(path) - 1):
            if graph.edge[path[i]][path[i + 1]]['in_use']:
                return False
        return True

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

        if state.over:
            return []

        # past_orders = list(set(self.old_pending_orders) - set(state.get_active_orders()))
        # expired_orders = []
        # for order in self.old_pending_orders:
        #     for currentOrder in state.get_active_orders():
        #         if order.get_node() == currentOrder.get_node():
        #             break
        #     pass


        commands = []
        if not self.built_station:
            commands.append(self.build_command(self.station))
            self.built_station = True

        # Copy graph and remove taken nodes
        free_graph = state.get_graph().copy()
        for active_order in state.get_active_orders():
            active_order_nodes = active_order[1]
            for i in range(0, len(active_order_nodes) - 1):
                free_graph.remove_edge(active_order_nodes[i], active_order_nodes[i + 1])

        # Go through orders from most to least value
        for order in reversed(sorted(state.get_pending_orders(), key=state.money_from)):
            try:
                path = nx.shortest_path(free_graph, self.station, order.get_node())
                # Remove edge from free graph if path is being used
                for i in range(0, len(path) - 1):
                    free_graph.remove_edge(path[i], path[i + 1])
                commands.append(self.send_command(order, path))
            except nx.NetworkXNoPath:
                print("Order is unreachable right now.")

        self.old_pending_orders = list(state.get_pending_orders())


        return commands

    def get_init_stations(self, state):
        stations = 1
        money_left = STARTING_MONEY - INIT_BUILD_COST

        while money_left >= INIT_BUILD_COST * math.pow(BUILD_FACTOR, stations):
            money_left -= INIT_BUILD_COST * math.pow(BUILD_FACTOR, stations)
            stations += 1

        return stations

    def init_station_build(self, state):

        while(self.get_init_stations() > 1)
            graph_ecc = state.get_graph().eccentricity(nx)
            diameter = state.get_graph().diameter(nx)
            radius = state.get_graph().radius(nx)

            nx.random
