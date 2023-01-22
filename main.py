from BayesNetwork import BayesNetwork
from Graph import Graph
from util import read_file

if __name__ == '__main__':
    path = r"env4.json"
    data = read_file(path)
    # get the vertices
    vertices = data["V"]
    # get the edges
    edges = data["E"]
    w = data["W"]
    graph = Graph(vertices.keys(), edges)
    # bayes network of the graph
    # get p1 and p2 from the user
    p1 = float(input("Enter p1: "))
    p2 = float(input("Enter p2: "))
    # p1 = 0.2
    # p2 = 0.3
    bayes = BayesNetwork(graph, vertices, p1, p2, w)
    # get the evidence from the user
    evidence = bayes.get_evidence_from_user()
    # evidence = bayes.get_evidence_from_string(
    #     "B(1)=0,B(2)=U,B(3)=1,B(4)=1,E(1)=U,E(2)=U,E(3)=U,E(4)=U,Weather=extreme")
    # print the probabilities
    print("The evidence is: {}".format(evidence))
    print("The probability of each vertex being broken is: {}".format(bayes.get_broken_prob(evidence)))
    print("The probability of each vertex containing people is: {}".format(bayes.get_people_prob(evidence)))
    print("The probability of the weather is: {}".format(bayes.get_weather_prob(evidence)))
