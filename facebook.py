from graph.graph import Graph

def gain(K, Z, vModify, g, list):
    """ calcoliamo il guadagno tra il set X-Z e Z.

    Args:
        K (set): insieme dove è stato rimosso v
        Z (set): insieme dove è stato aggiunto v
        vModify (vertex):  nodo che aggiungiamo/togliamo per valutarne il guadagno
        g (graph): grafo con tutti i collegamenti
        list (list): lista di tutti i nodi

    Returns:
        [number]: ritorna il guadagno calcolato tra x-z e z
    """
    weight = 0
    vModify = list[vModify]
    for e in g.incident_edges(vModify):
        if e._origin != vModify and e._origin._element in K:
            weight += e.element() #sommo tutti i pesi degli archi che uniscono k con i veritici z
        elif e._destination != vModify and e._destination._element in K:
            weight += e.element() 
        elif e._origin != vModify and e._origin._element in Z:
            weight -= e.element()
        elif e._destination != vModify and e._destination._element in Z:
            weight -= e.element()

    return weight


def calcA(V, Z, vModify, g, list):
    """un interfaccia che richiama la funzione gain
    """
    return gain(V, Z, vModify, g, list)

def calcB(V, Z, vModify, g, list):
    """un interfaccia che richiama la funzione gain
    """
    return gain(Z, V, vModify, g, list)


def facebook_enmy(V, E):
    """Lo strumento di Facebook raggruppa gli elettori per Democratici e Repubblicani in 
    modo che il livello di inimicizia all'interno di ogni gruppo sia basso, e il livello di inimicizia tra i due gruppi sia il più grande possibile.

    Args:
        V ([type]): insieme di elettori
        E (dict): dizionario che contine le coppie di elettori che hanno una relazione di amicizia su Facebook, e il loro valore corrisponde all'enmy

    Returns:
        restituisce due insiemi, D e R, che corrispondono rispettivamente agli elettori dei Democratici e dei Repubblicani.
    """
    g = Graph()
    list = {}
    D = set()
    VminusD = V.copy()
    T = V.copy()
    VminusT = set()

    # inserisco i vertici nel grafo e li salvo all'interno di una lista
    for v in V:
        list[v] = g.insert_vertex(v)

    # aggiungo tutti gli archi al grafo
    for e in E.keys():
        g.insert_edge(list[e[0]], list[e[1]], E.get(e))

    # scorro tutti i vertici
    for v in V:
        # inizializzo tutte le variabili da utilizzare nei calcoli
        a = 0
        b = 0

        # aggiungo temporaneamente il vertice corrente all'interno del set, ne valuto il guadagno e lo rimuovo
        D.add(v)
        VminusD.remove(v)
        a = calcA(VminusD, D, v, g, list)
        D.remove(v)
        VminusD.add(v)

        # rimuovo v temporaneamente per calcolare il guadagno, per poi riaggiungerlo
        T.remove(v)
        VminusT.add(v)
        b = calcB(VminusT, T, v, g, list)
        T.add(v)
        VminusT.remove(v)

        # se aggiungendo i vertice ho un gadagno maggiore lo aggiungo all'elenco dei democratici e lo rimuovo dalla lista, altrimenti il contrario
        if (a >= b):
            D.add(v)
            VminusD.remove(v)
        else:
            T.remove(v)
            VminusT.add(v)

    # ritorno il set di democratici e di rep(è la differenza dell'elenco completo con quello dei dem)
    R = V - D
    return D, R


def myBFS(g, s, discovered, d):
    """BFS personalizzata, si ferma appena trova il primo percorso possibile per la mia destinazione

    Args:
        g (graph): grafo
        s (vertex): sorgente
        discovered (dict): dict dove salvare il path
        d (vertex): destinazione
    """
    level = [s]  # first level includes only s
    while len(level) > 0:
        next_level = []  # prepare to gather newly found vertices
        for u in level:
            finalEdge = g.get_edge(u, d)
            if(finalEdge is not None):
                # if che serve per bloccare il ciclo se trova il path che parte da S e arriva a D
                if finalEdge._element != 0:
                    discovered[d] = finalEdge  # e is the tree edge that discovered v
                    return
            for e in g.incident_edges(u):  # for every outgoing edge from u
                if e._element != 0:
                    v = e.opposite(u)
                    if v not in discovered:  # v is an unvisited vertex
                        discovered[v] = e  # e is the tree edge that discovered v
                        next_level.append(v)  # v will be further considered in next pass

        level = next_level  # relabel 'next' level to become current


def facebook_friend(V, E):
    """Lo strumento di Facebook ha ora bisogno di raggruppare gli elettori per Democratici e Repubblicani in modo che il
    livello di amicizia all'interno di ogni gruppo sia grande, e il livello di amicizia tra i due 
    gruppi sia il più basso possibile.

    """
    G = Graph(True)
    Nodes = {}
     
    # inseriamo i vertici dem e rep, aggiungiamo i vari vertici nel grafo e li colleghiamo con le rispettive probabilità a dem e rep
    Dem = G.insert_vertex("Dem")
    Rep = G.insert_vertex("Rep")

    for v in V:
        toIns = G.insert_vertex(v)
        Nodes[v] = toIns
        # inseriamo tutti gli edge che abbiamo e per ognuno mettiamo anche l'opposto 
        G.insert_edge(Dem, toIns, V[v][0])
        G.insert_edge(toIns, Dem, 0)
        G.insert_edge(toIns, Rep, V[v][1])
        G.insert_edge(Rep, toIns, 0)

    for e in E:
        G.insert_edge(Nodes.get(e[0]), Nodes.get(e[1]), E[e])
        G.insert_edge(Nodes.get(e[1]), Nodes.get(e[0]), E[e])

    # diction conterrà tutto quello che ci restituisce la mybfs, il path da un nodo ad un altro, 
    # nel nostro caso ci restituisce un solo percorso tra quelli possibili (da dem a rep)
    diction = {}    
    diction[Dem] = None
    myBFS(G, Dem, diction, Rep)
    
    # lo faccio fino a quando dem riesce ad arrivare a rep, se non ci arrivo significa che ho finito la divisione dei partiti
    while diction.get(Rep) is not None:
        edge = diction.get(Rep)
        min = edge.element()

        # calcolo del minimo per tutto il path
        while edge is not None:
            if (edge.element() < min):
                min = edge.element()
            edge = diction.get(edge._origin)

        # aggiorno i pesi dei collegamenti
        edge = diction.get(Rep)
        while edge is not None:
            edge._element -= min
            G.get_edge(edge._destination, edge._origin)._element += min
            edge = diction.get(edge._origin)

        diction = {}
        diction[Dem] = None

        myBFS(G, Dem, diction, Rep)

    D = set()

    # aggiungo tutti gli elementi attacati alla partizione d
    for key in diction.keys():
        if key.element() != 'Dem': #dem non deve essere calcolato nella  soluzione per questo motivo lo escludiamo
            D.add(key.element())

    R = Nodes.keys() - D

    return D, R


if __name__ == "__main__":
    V = {'A': (4, 1), 'B': (5, 0), 'C': (0, 5), 'D': (1, 4)}
    E = {('A', 'B'): 5, ('A', 'C'): 1, ('A', 'D'): 2, ('B', 'C'): 2, ('D', 'B'): 1, ('C', 'D'): 5}
    """V = {'A': (1, 0), 'B': (3, 2), 'C': (1, 3), 'D': (2, 1), 'E': (2,4)}
    E = {('A', 'B'): 2, ('A', 'C'): 4, ('B', 'D'): 3, ('C', 'D'): 5, ('D', 'E'): 3}"""

    """V = {'A': (4, 0), 'B': (5, 0), 'C': (0, 0), 'D': (1, 0)}
    E = {('A', 'B'): 5, ('A', 'C'): 1, ('A', 'D'): 2, ('B', 'C'): 2, ('D', 'B'): 1, ('C', 'D'): 5}"""

    
    """V = {'A', 'B', 'C', 'D', 'E'}
    E = {('A', 'B'): 2, ('A', 'C'): 4, ('B', 'D'): 3, ('C', 'D'): 5, ('D', 'E'): 3}"""

    D, R = facebook_friend(V, E)
    
    print(str(D) + " " + str(R))
