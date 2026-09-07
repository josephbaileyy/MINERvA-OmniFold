#!/usr/bin/env python3
"""A minimal fake of the PyROOT surface this producer uses. TEST SUPPORT ONLY.

It exists so the tests can drive the PRODUCER rather than hand-write report records.
Hand-written records only ever prove that the validator classifies what the test author
already believed; running the real producer against a controllable file tree proves that
the payloads the validator classifies are the ones the producer actually emits.

It implements exactly what ``pm_root_inspect`` touches: ``gROOT``, ``TFile.Open``,
``IsZombie``, ``GetListOfKeys``, ``Get``, ``Close``, and enough of ``TH1``/``TNamed``/
``TParameter`` to be read the way the producer reads them.  Nothing here is a ROOT
substitute for any other purpose.
"""
from __future__ import annotations


class FakeKey:
    def __init__(self, name, class_name="TObject", cycle=1):
        self._name, self._class, self._cycle = name, class_name, cycle

    def GetName(self):
        return self._name

    def GetClassName(self):
        return self._class

    def GetCycle(self):
        return self._cycle


class FakeNamed:
    """Stands in for a TNamed whose payload is its title."""

    def __init__(self, title, class_name="TNamed"):
        self._title, self._class = title, class_name

    def ClassName(self):
        return self._class

    def GetTitle(self):
        return self._title


class FakeParameter:
    """Stands in for TParameter<double>, whose value is in GetVal(), not GetTitle()."""

    def __init__(self, value):
        self._value = value

    def ClassName(self):
        return "TParameter<double>"

    def GetVal(self):
        return self._value

    def GetTitle(self):
        return "this is a title, not the number"


class FakeHist:
    def __init__(self, contents, low_edges=None, width=1.0):
        self._contents = list(contents)
        self._low = low_edges

    def ClassName(self):
        return "TH1D"

    def GetNbinsX(self):
        return len(self._contents)

    def GetBinContent(self, one_based):
        return self._contents[one_based - 1]

    def GetBinLowEdge(self, one_based):
        return (self._low[one_based - 1] if self._low is not None
                else float(one_based - 1))

    def GetBinWidth(self, one_based):
        return 1.0

    def GetEntries(self):
        return len(self._contents)


class FakeFile:
    def __init__(self, objects, zombie=False):
        #: name -> object, or name -> None for a key that lists but will not load
        self._objects = dict(objects)
        self._zombie = zombie
        self.closed = False

    def __bool__(self):
        return True

    def IsZombie(self):
        return self._zombie

    def GetListOfKeys(self):
        return [FakeKey(name, type(obj).__name__ if obj is not None else "TObject")
                for name, obj in self._objects.items()]

    def Get(self, name):
        return self._objects.get(name)

    def Close(self):
        self.closed = True


class FakeROOT:
    """The module object installed as ``sys.modules['ROOT']``."""

    kWarning = 1001
    kFatal = 6000

    def __init__(self, files_by_path):
        self._files = files_by_path
        self.gErrorIgnoreLevel = 0

        outer = self

        class _GROOT:
            @staticmethod
            def SetBatch(value):
                outer.batch = value

            @staticmethod
            def GetVersion():
                return "fake-6.28/12"

        class _TFile:
            @staticmethod
            def Open(path, mode):
                assert mode == "READ", "the inspection must open READ"
                return outer._files.get(str(path))

        self.gROOT = _GROOT()
        self.TFile = _TFile()
