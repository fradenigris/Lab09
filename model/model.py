from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO
import copy

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = 0
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        self._tour_setAttrazioni = {}
        self._attrazione_setTour = {}

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # TODO

        id_tutti_tour = self.tour_map.keys()
        self._tour_setAttrazioni = {item : set() for item in id_tutti_tour}

        for id_tour in self._tour_setAttrazioni.keys():
            ciao = TourDAO.get_tour_attrazioni(id_tour)
            for el in ciao:
                self._tour_setAttrazioni[id_tour].add(el['id_attrazione'])

        id_tutte_attrazioni = self.attrazioni_map.keys()
        self._attrazione_setTour = {item : set() for item in id_tutte_attrazioni}

        for id_tour in self._tour_setAttrazioni.keys():
            ciao = TourDAO.get_tour_attrazioni(id_tour)
            for id_attrazione in self._attrazione_setTour.keys():
                for el in ciao:
                    if id_attrazione == el['id_attrazione']:
                        self._attrazione_setTour[id_attrazione].add(el['id_tour'])

    def _calcola_valore_tour(self):
        for tour in self.tour_map.values():
            valore = 0
            if tour.id in self._tour_setAttrazioni:
                for id_attr in self._tour_setAttrazioni[tour.id]:
                    if id_attr in self.attrazioni_map:
                        valore += self.attrazioni_map[id_attr].valore_culturale
            tour.valore = valore

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = 0

        # TODO

        self._calcola_valore_tour()

        # Tour filtrati secondo la regione passata come parametro alla funzione (regione selezionata nel Dropdown)
        tour_filtrati = [t for t in self.tour_map.values() if t.id_regione == id_regione]

        self._ricorsione(
            start_index = 0,
            pacchetto_parziale = list(),
            durata_corrente = 0,
            costo_corrente = 0,
            valore_corrente = 0,
            attrazioni_usate = set(),
            lista_tour = tour_filtrati,
            max_giorni = max_giorni,
            max_budget = max_budget
        )

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list,
                    durata_corrente: int, costo_corrente: float, valore_corrente: int,
                    attrazioni_usate: set, lista_tour: list,
                    max_giorni: int, max_budget: float):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno

        if start_index == len(lista_tour):
            if valore_corrente > self._valore_ottimo:
                self._valore_ottimo = valore_corrente
                self._pacchetto_ottimo = copy.deepcopy(pacchetto_parziale)
                self._costo = costo_corrente
            return

        tour_corrente = lista_tour[start_index]
        attrazioni_tour_corrente = self._tour_setAttrazioni[tour_corrente.id]

        if max_budget is None:
            check_budget = True
        else:
            if costo_corrente + tour_corrente.costo <= max_budget:
                check_budget = True
            else:
                check_budget = False

        if max_giorni is None:
            check_durata = True
        else:
            if durata_corrente + tour_corrente.durata_giorni <= max_giorni:
                check_durata = True
            else:
                check_durata = False

        if len(attrazioni_usate.intersection(attrazioni_tour_corrente)) == 0:
            check_attrazioni = True
        else:
            check_attrazioni = False

        if check_budget and check_durata and check_attrazioni:
            pacchetto_parziale.append(tour_corrente)
            nuove_attrazioni_usate = attrazioni_usate | attrazioni_tour_corrente

            self._ricorsione(
                start_index + 1,
                pacchetto_parziale,
                durata_corrente + tour_corrente.durata_giorni,
                costo_corrente + tour_corrente.costo,
                valore_corrente + tour_corrente.valore,
                nuove_attrazioni_usate,
                lista_tour,
                max_giorni,
                max_budget
            )
            pacchetto_parziale.pop()

        self._ricorsione(
            start_index + 1,
            pacchetto_parziale,
            durata_corrente,
            costo_corrente,
            valore_corrente,
            attrazioni_usate,
            lista_tour,
            max_giorni,
            max_budget
        )


