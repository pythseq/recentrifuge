"""
Classes with statistical data

"""

from statistics import mean
from typing import NamedTuple, Dict, List, Union, Type, Optional, overload

from recentrifuge.config import Score, NO_SCORE, Id


class NT(int):
    """Class representing any chain of nucleotides"""

    def __str__(self) -> str:
        """Format nucleotides number with SI prefixes and units"""
        value: float
        unit: str
        if self > 1e+12:
            value = self / 1e+12
            unit = 'Tnt'
        elif self > 1e+9:
            value = self / 1e+9
            unit = 'Gnt'
        elif self > 1e+6:
            value = self / 1e+6
            unit = 'Mnt'
        elif self > 1e+3:
            value = self / 1e+3
            unit = 'knt'
        else:
            value = self
            unit = 'nt'
            return f'{value:d} {unit}'
        return f'{value:.2f} {unit}'


# pylint: disable=too-few-public-methods
class SeqsStats(NamedTuple):
    """Sequence statistics"""
    read: int = 0
    unclas: int = 0
    clas: int = 0
    filt: int = 0



class ScoreStats(NamedTuple):
    """Score statistics"""
    maxi: Score = NO_SCORE
    mean: Score = NO_SCORE
    mini: Score = NO_SCORE


class LengthStats(NamedTuple):
    """Leg statistics"""
    maxi: NT = NT(0)
    mean: NT = NT(0)
    mini: NT = NT(0)
# pylint: enable=too-few-public-methods


# pylint: disable=function-redefined, unused-argument
@overload
def stats(dict_list: Dict[Id, List[Score]],
          tuple_cls: Type[ScoreStats],
          elems_cls: Type[Score]) -> ScoreStats:
    """PEP-484 overload: ScoreStats and Score"""
    pass


@overload
def stats(dict_list: Dict[Id, List[int]],
          tuple_cls: Type[LengthStats],
          elems_cls: Type[NT]) -> LengthStats:
    """PEP-484 overload: LengthStats and NT"""
    pass


def stats(dict_list, tuple_cls, elems_cls):
    """Get minimum, mean and maximum of dictionary of list"""
    return (tuple_cls(
        mini=elems_cls(min([min(e) for e in dict_list.values()])),
        mean=elems_cls(mean([mean(e) for e in dict_list.values()])),
        maxi=elems_cls(max([max(e) for e in dict_list.values()]))
    ))
# pylint: enable=function-redefined, unused-argument


class SampleStats(object):
    """Sample statistics"""

    def __init__(self, is_ctrl: bool = False,
                 minscore: Score = None, nt_read: int = 0,
                 seq_read: int = 0, seq_filt: int = 0,
                 seq_clas: int = None, seq_unclas: int = 0,
                 lens: Dict[Id, List[int]] = None,
                 scores: Dict[Id, List[Score]] = None,
                 scores2: Dict[Id, List[Score]] = None,
                 scores3: Dict[Id, List[Score]] = None,
                 ) -> None:
        """Initialize some data and set up data structures"""
        self.is_ctrl: bool = is_ctrl
        self.minscore: Optional[Score] = minscore
        self.nt_read: NT = NT(nt_read)
        self.seq: SeqsStats
        if seq_clas is not None:
            self.seq = SeqsStats(
                read=seq_read, unclas=seq_read - seq_clas,
                clas=seq_clas, filt=seq_filt)
        else:
            self.seq = SeqsStats(
                read=seq_read, unclas=seq_unclas,
                clas=seq_read - seq_unclas, filt=seq_filt)
        if lens is not None:
            self.len: LengthStats = stats(lens, LengthStats, NT)
        else:
            self.len = LengthStats()
        if scores is not None:
            self.sco: ScoreStats = stats(scores, ScoreStats, Score)
            self.num_taxa: int = len(scores)
        else:
            self.sco = ScoreStats()
            self.num_taxa = 0
        if scores2 is not None:
            self.sco2: ScoreStats = stats(scores2, ScoreStats, Score)
        if scores3 is not None:
            self.sco3: ScoreStats = stats(scores3, ScoreStats, Score)

    def to_dict(self) -> Dict[str, Union[int, Score, None]]:
        """
        Create a dict with the data of the object (used to feed a DataFrame)
        """
        return {'Seqs. read': self.seq.read, 'Seqs. unclass.': self.seq.unclas,
                'Seqs. class.': self.seq.clas, 'Seqs. filtered': self.seq.filt,
                'Score min': self.sco.mini, 'Score mean': self.sco.mean,
                'Score max': self.sco.maxi, 'Length min': self.len.mini,
                'Length mean': self.len.mean, 'Length max': self.len.maxi,
                'Total nt read': self.nt_read, 'Taxa assigned': self.num_taxa,
                'Score limit': self.minscore}

    def to_krona(self) -> Dict[str, str]:
        """
        Create a dict with the data of the object (used to feed a Krona plot)
        """
        return {'isctr': str(self.is_ctrl),
                'sread': str(self.seq.read),
                'sclas': str(self.seq.clas),
                'sfilt': str(self.seq.filt),
                'scmin': str(self.sco.mini),
                'scavg': str(self.sco.mean),
                'scmax': str(self.sco.maxi),
                'lnmin': str(self.len.mini),
                'lnavg': str(self.len.mean),
                'lnmax': str(self.len.maxi),
                'taxas': str(self.num_taxa),
                'sclim': str(self.minscore),
                'totnt': str(self.nt_read)}

    def get_unclas_ratio(self) -> float:
        """Get ratio of unclassified sequences"""
        return self.seq.unclas / self.seq.read

    def get_reject_ratio(self) -> float:
        """Get ratio of rejected sequences by filtering"""
        return 1 - self.seq.filt / self.seq.clas
