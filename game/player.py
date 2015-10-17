import time
import copy
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

        start = time.time()

        # Region setup
        g = state.get_graph()
        regions = max(self.build_num(state), 2)
        # regions =
        print("regions ", regions)
        for node in g.nodes():
            g.node[node]['region'] = -1

        # Generate n random, unique points
        origins = []
        for i in range(0, regions):
            node = random.choice(g.nodes())
            while node in origins:
                node = random.choice(g.nodes())
            g.node[node]['region'] = i
            origins.append(node)

        # Create initial boundary lists
        boundaries = []
        for i in range(0, regions):
            boundary = [origins[i]]
            boundaries.append(boundary)

        # Grow regions
        graph_full = False
        while not graph_full:
            for i in range(0, regions):
                new_boundary = []
                for node in boundaries[i]:
                    # Find all neighbors not currently claimed and claim them
                    for neighbor in [x for x in g.neighbors(node) if g.node[x]['region'] == -1]:
                        g.node[neighbor]['region'] = i
                        new_boundary.append(neighbor)
                boundaries[i] = new_boundary
            graph_full = True
            for node in g.nodes():
                if g.node[node]['region'] == -1:
                    graph_full = False

        # Find nodes at center of regions
        self.stations = []
        sorted_centers = sorted(nx.closeness_centrality(state.get_graph()).items(), key=operator.itemgetter(1))
        self.stations.append(sorted_centers[-1][0])
        for i in range(0, regions):
            regional_graph = g.copy()
            for node in regional_graph.nodes():
                if regional_graph.node[node]['region'] != i:
                    regional_graph.remove_node(node)
            sorted_centers = sorted(nx.closeness_centrality(regional_graph).items(), key=operator.itemgetter(1))
            self.stations.append(sorted_centers[-1][0])

        self.constructed_stations = 0
        self.old_pending_orders = []
        self.expired_orders = []
        self.built_station_one = False
        self.built_station_two = False
        self.built_station_three = False

        print("Setup Time: ", time.time() - start)

    # # Checks if we can use a given path
    # def path_is_valid(self, state, path):
    #     graph = state.get_graph()
    #     for i in range(0, len(path) - 1):
    #         if graph.edge[path[i]][path[i + 1]]['in_use']:
    #             return False
    #     return True

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

        start = time.time()

        # Diagnostic code
        # active_order_nodes = [currentOrder[0] for currentOrder in state.get_active_orders()]
        # for order in self.old_pending_orders:
        #     # Forget order if it still exists
        #     if order.get_node() in active_order_nodes:
        #         break
        #     # Forget order if it still had money
        #     if state.money_from(order) - DECAY_FACTOR > 0:
        #         break
        #     self.expired_orders.append(order)
        # if state.get_time() >= 999:
        #     print("Lost Orders: ", len(self.expired_orders))
        #     print ("Lost Cash: ", sum([order.money for order in self.expired_orders]))
        #     for order in sorted(self.expired_orders, key=lambda x: x.node):
        #         print(order)
        #self.old_pending_orders = list(state.get_pending_orders())

        commands = []

        #Build first station and then second
        # if not self.built_station_one:
        #     commands.append(self.build_command(self.stations[0]))
        #     self.built_station_one = True
        #     self.constructed_stations = 1
        # if not self.built_station_two and state.get_money() >= 1500:
        #     commands.append(self.build_command(self.stations[1]))
        #     self.built_station_two = True
        #     self.constructed_stations = 2
        # if not self.built_station_three and state.get_money() >= 2250:
        #     commands.append(self.build_command(self.stations[2]))
        #     self.built_station_three = True
        #     self.constructed_stations = 3

        required_money = int(1000.0 * pow(BUILD_FACTOR, self.constructed_stations))
        print(required_money)
        print(state.get_money())
        print(self.constructed_stations)
        print(len(self.stations))
        if self.constructed_stations < len(self.stations) and state.get_money() >= required_money:
            commands.append(self.build_command(self.stations[self.constructed_stations]))
            self.constructed_stations += 1

        # Copy graph and remove edges currently being used for paths
        free_graph = state.get_graph().copy()
        for active_order in state.get_active_orders():
            active_order_nodes = active_order[1]
            for i in range(0, len(active_order_nodes) - 1):
                free_graph.remove_edge(active_order_nodes[i], active_order_nodes[i + 1])

        evaluated_orders = []
        for station in self.stations[0:self.constructed_stations]:
            for order in state.get_pending_orders():
                order = copy.copy(order)
                try:
                    order.station = station
                    order.path = nx.shortest_path(free_graph, station, order.get_node())
                    order.worth = state.money_from(order) - (len(order.path) * DECAY_FACTOR)
                    evaluated_orders.append(order)
                except nx.NetworkXNoPath:
                    print("No path found for order from station.")
        evaluated_orders = sorted(evaluated_orders, key=lambda x: x.worth, reverse=True)
        print(evaluated_orders)

        while len(evaluated_orders) > 0:
            # Remove edge from free graph and issue command
            order = evaluated_orders[0]
            for i in range(0, len(order.path) - 1):
                free_graph.remove_edge(order.path[i], order.path[i + 1])
            commands.append(self.send_command(order, order.path))

            # Re-calculate worth of orders and remove impossible ones, then re-sort
            new_evaluated_orders = []
            for o in [x for x in evaluated_orders if x.get_node() != order.get_node()]:
                try:
                    o.path = nx.shortest_path(free_graph, o.station, o.get_node())
                    o.worth = state.money_from(o) - (len(o.path) * DECAY_FACTOR)
                    new_evaluated_orders.append(o)
                except nx.NetworkXNoPath:
                    print("No path found for order from station.")
            evaluated_orders = sorted(new_evaluated_orders, key=lambda x: x.worth, reverse=True)

        print("Step Time: ", time.time() - start)

        return commands

    # def get_init_stations(self, state):
    #     stations = 1
    #     money_left = STARTING_MONEY - INIT_BUILD_COST
    #
    #     while money_left >= INIT_BUILD_COST * math.pow(BUILD_FACTOR, stations):
    #         money_left -= INIT_BUILD_COST * math.pow(BUILD_FACTOR, stations)
    #         stations += 1
    #
    #     return stations
    #
    # def init_station_build(self, state):
    #
    #     while(self.get_init_stations() > 1)
    #         graph_ecc = state.get_graph().eccentricity(nx)
    #         diameter = state.get_graph().diameter(nx)
    #         radius = state.get_graph().radius(nx)
    #
    #         nx.random

    stations = 1

    def get_init_stations(self, state):
        stations = 1
        money_left = STARTING_MONEY - INIT_BUILD_COST

        while money_left >= INIT_BUILD_COST * math.pow(BUILD_FACTOR, stations):
            money_left -= INIT_BUILD_COST * math.pow(BUILD_FACTOR, stations)
            stations += 1

        return stations

    def init_station_build(self, state):
        pass

    def should_build(self, state, stn):
        diameter = nx.diameter(state.get_graph())
        cost_of_station = INIT_BUILD_COST * math.pow(BUILD_FACTOR, stn)
        profit = ORDER_CHANCE * GAME_LENGTH * DECAY_FACTOR * (diameter/(4 * math.sqrt(stn)) - diameter/(4 * math.sqrt(stn + 1)))
        return profit > cost_of_station * 2

    def build_num(self, state):
        stn = 1
        while self.should_build(state, stn):
            stn += 1
        return stn - 1