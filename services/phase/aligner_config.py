from .config import Config
from .sql_config import SQLConfig


# aligner config
class AlignerConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # File matching config
        self.file_match_config = {
            "Default": {
                "Default": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": [
                                    "\\d+L(\\d+|R|A)-\\d+",
                                    "Lower",
                                    "lower",
                                    "Mandibular",
                                    "mandibular",
                                ],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": [
                                    "\\d+U(\\d+|R|A)-\\d+",
                                    "Upper",
                                    "upper",
                                    "Maxillary",
                                    "maxillary",
                                    "Maxillar",
                                    "maxillar",
                                ],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "(U|L)\\d+",
                                    "step \\d+",
                                    "Step \\d+",
                                    "step-\\d+",
                                    "Step_\\d+",
                                    "step_\\d+",
                                    "Step-\\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "stage-\\d+",
                                    "Stage-\\d+",
                                    "Subsetup\\d+",
                                    "subsetup\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "SSCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "Subsetup\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "SSCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Step 0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "SSR": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["Retainer", "RETAINER"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "TSCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Step 0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "OFCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Step 0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "POCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower", "Mandibular", "mandibular"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": [
                                    "Upper",
                                    "upper",
                                    "Maxillary",
                                    "maxillar",
                                    "Maxillar",
                                    "maxillary",
                                ],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "Step-\\d+",
                                    "step-\\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "aligner_\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "POCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower", "Mandibular", "mandibular"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": [
                                    "Upper",
                                    "upper",
                                    "Maxillar",
                                    "maxillar",
                                    "Maxillary",
                                    "maxillary",
                                ],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Step 0", "attachments", "attachment"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "PLCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Step 0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "POR": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["Retainer", "RETAINER", "retainer"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "POR-2": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["Retainer", "RETAINER", "retainer"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "SSR-2": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["Retainer", "RETAINER", "retainer"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "Strayt - 1365": {
                "STCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "step-\\d+",
                                    "Step-\\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "stage-\\d+",
                                    "Stage-\\d+",
                                    "Subsetup\\d+",
                                    "subsetup\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "STR": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["Retainer", "RETAINER", "retainer"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "Brius Technol - 1076": {
                "Default": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["L"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["U"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "U\\d+_",
                                    "L\\d+_",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "BCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["L"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["U"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["U0", "L0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "ORTHOFX - 1117": {
                "Default": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "(U|L)\\d+",
                                    "step \\d+",
                                    "Step \\d+",
                                    "step_\\d+",
                                    "Step_\\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "aligner_\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "Z1": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "(U|L)\\d+",
                                    "step \\d+",
                                    "Step \\d+",
                                    "Step_\\d+",
                                    "step_\\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "aligner_\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "Z1AT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": [
                                    "(U|L)(\\d+|)(A)",
                                    "stage_00_AT",
                                    "stage_00",
                                    "aligner_00",
                                    "00_AT",
                                ],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "ZR1": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["(U|L)(\\d+|)(R)", "retainer", "ret", "raw"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "ZR2": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["(U|L)(\\d+|)(R)", "retainer", "ret", "raw"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "TBR1": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["(U|L)(\\d+|)(R)", "retainer", "ret", "raw"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "Dandy - 1341": {
                "Default": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 1,
                                "DefaultValue": "L",
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "(U|L)\\d+",
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "DCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "(U|L)\\d+",
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "aligner_\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "DAR1": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": [
                                    "(U|L)(\\d+|)(R)",
                                    "Retainer",
                                    "RETAINER",
                                    "retainer",
                                ],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "DAR.76": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": [
                                    "(U|L)(\\d+|)(R)",
                                    "Retainer",
                                    "RETAINER",
                                    "retainer",
                                ],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "DARE": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": [
                                    "(U|L)(\\d+|)(R)",
                                    "Retainer",
                                    "RETAINER",
                                    "retainer",
                                ],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "DCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["\\d+L(\\d+|R|A)-\\d+", "Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["\\d+U(\\d+|R|A)-\\d+", "Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": [
                                    "(U|L)(\\d+|)(A)",
                                    "Subsetup0",
                                    "attachment_template",
                                    "template_00",
                                ],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "Quality NZ": {
                "Default": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "QDCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "Subsetup\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "QDAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Template", "Step 0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "QDR": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["Retainer", "RETAINER", "retainer"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "Quality AU 1195": {
                "Default": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "QDCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "Subsetup\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "QDAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Template", "Step 0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "QDR": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["Retainer", "RETAINER", "retainer"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "Ottawa - 1111": {
                "Default": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "SSCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "Subsetup\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "SSCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Step 0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
                "SSR": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "R",
                                "Terms": ["Retainer", "RETAINER"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "Derby 1295": {
                "Default": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "TSCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "Subsetup\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "TSCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Step 0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "OraPharma - 1359": {
                "Default": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "OFCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "Subsetup\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "OFCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Step 0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "Your Smile Factor": {
                "Default": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "PLCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "step \\d+",
                                    "Step \\d+",
                                    "stage_\\d+",
                                    "Stage_\\d+",
                                    "stage \\d+",
                                    "Stage \\d+",
                                    "Subsetup\\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "PLCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Step 0"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
            "Menzies - 1132": {
                "POCA": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": ["Upper", "upper"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "\\d+",
                                "Terms": [
                                    "Lower \\d+",
                                    "lower \\d+",
                                    "Upper \\d+",
                                    "upper \\d+",
                                ],
                                "SearchTermResultWithValue": True,
                                "MinimumDigits": 2,
                                "DefaultValue": "0",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 0,
                },
                "POCAT": {
                    "Identifiers": [
                        [
                            {
                                "Value": "L",
                                "Terms": ["Lower", "lower", "Mandibular", "mandibular"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                            {
                                "Value": "U",
                                "Terms": [
                                    "Upper",
                                    "upper",
                                    "Maxillar",
                                    "maxillar",
                                    "Maxillary",
                                    "maxillary",
                                ],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            },
                        ],
                        [
                            {
                                "Value": "A",
                                "Terms": ["Lower 0", "Upper 0", "attachment"],
                                "SearchTermResultWithValue": False,
                                "MinimumDigits": 0,
                                "DefaultValue": "",
                                "Weight": 2,
                            }
                        ],
                    ],
                    "Removed": [],
                    "WeightModifier": 1,
                },
            },
        }

        # # Aligner functions
        # input: Extension, AlignerID
        # output: [[Name]]
        self.name_importer = "SELECT CONCAT(b.CaseNumber, a.Step, '-', a.AlignerID, '.', (SELECT Extension FROM {database}.dbo.FileTypes WHERE ID = ?)) as Name, a.AlignerID FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and AlignerID in (SELECT value FROM STRING_SPLIT(?, ','))"

        # # Aligners Template
        self.aligners_template = """
            SELECT
            aligners_table.*,
            cases_table.CaseNumber,
            cases_table.CustomerID,
            baglinks.ID as LinkID, 
            baglinks.BagUDID, 
            bags.PatientName, 
            bags.DoctorName, 
            bags.LegibleStep, 
            bags.Steps, 
            bags.GTIN, 
            bags.LotNumber as BagLotID, 
            bags.SerialNumber, 
            bags.Barcode, 
            bags.MDate, 
            bags.EDate, 
            bags.Created as BagCreated, 
            bags.CreatedID as BagCreatedID, 
            fdaproduct.FDARegNumber, 
            fdaproduct.Category,
            fixits.Status as FixitStatus

            FROM
            (
                SELECT
                source_table.AlignerID,
                source_table.CaseID,
                source_table.Step,
                source_table.StepExtender,
                source_table.Remake,
                source_table.[Status],
                source_table.LotNumber,
                source_table.ProductID,
                source_table.FixitID,
                source_table.FixitCID,
                source_table.Created,
                source_table.CreatedID,
                source_table.CurrentLocation,
                MAX(CASE SubmissionLocation WHEN 34 THEN StationSubmissionDate END) as [Location-34-Created], 
                MAX(CASE SubmissionLocation WHEN 34 THEN StationSubmissionBy END) as [Location-34-CreatedBy],

                MAX(CASE SubmissionLocation WHEN 36 THEN StationSubmissionDate END) as [Location-36-Created], 
                MAX(CASE SubmissionLocation WHEN 36 THEN StationSubmissionBy END) as [Location-36-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 35 THEN StationSubmissionDate END) as [Location-35-Created], 
                MAX(CASE SubmissionLocation WHEN 35 THEN StationSubmissionBy END) as [Location-35-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 3 THEN StationSubmissionDate END) as [Location-3-Created], 
                MAX(CASE SubmissionLocation WHEN 3 THEN StationSubmissionBy END) as [Location-3-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 4 THEN StationSubmissionDate END) as [Location-4-Created], 
                MAX(CASE SubmissionLocation WHEN 4 THEN StationSubmissionBy END) as [Location-4-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 5 THEN StationSubmissionDate END) as [Location-5-Created], 
                MAX(CASE SubmissionLocation WHEN 5 THEN StationSubmissionBy END) as [Location-5-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 2 THEN StationSubmissionDate END) as [Location-2-Created], 
                MAX(CASE SubmissionLocation WHEN 2 THEN StationSubmissionBy END) as [Location-2-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 6 THEN StationSubmissionDate END) as [Location-6-Created], 
                MAX(CASE SubmissionLocation WHEN 6 THEN StationSubmissionBy END) as [Location-6-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 9 THEN StationSubmissionDate END) as [Location-9-Created], 
                MAX(CASE SubmissionLocation WHEN 9 THEN StationSubmissionBy END) as [Location-9-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 10 THEN StationSubmissionDate END) as [Location-10-Created], 
                MAX(CASE SubmissionLocation WHEN 10 THEN StationSubmissionBy END) as [Location-10-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 7 THEN StationSubmissionDate END) as [Location-7-Created], 
                MAX(CASE SubmissionLocation WHEN 7 THEN StationSubmissionBy END) as [Location-7-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 37 THEN StationSubmissionDate END) as [Location-37-Created], 
                MAX(CASE SubmissionLocation WHEN 37 THEN StationSubmissionBy END) as [Location-37-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 8 THEN StationSubmissionDate END) as [Location-8-Created], 
                MAX(CASE SubmissionLocation WHEN 8 THEN StationSubmissionBy END) as [Location-8-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 12 THEN StationSubmissionDate END) as [Location-12-Created], 
                MAX(CASE SubmissionLocation WHEN 12 THEN StationSubmissionBy END) as [Location-12-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 13 THEN StationSubmissionDate END) as [Location-13-Created], 
                MAX(CASE SubmissionLocation WHEN 13 THEN StationSubmissionBy END) as [Location-13-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 14 THEN StationSubmissionDate END) as [Location-14-Created], 
                MAX(CASE SubmissionLocation WHEN 14 THEN StationSubmissionBy END) as [Location-14-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 15 THEN StationSubmissionDate END) as [Location-15-Created], 
                MAX(CASE SubmissionLocation WHEN 15 THEN StationSubmissionBy END) as [Location-15-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 16 THEN StationSubmissionDate END) as [Location-16-Created], 
                MAX(CASE SubmissionLocation WHEN 16 THEN StationSubmissionBy END) as [Location-16-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 17 THEN StationSubmissionDate END) as [Location-17-Created], 
                MAX(CASE SubmissionLocation WHEN 17 THEN StationSubmissionBy END) as [Location-17-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 18 THEN StationSubmissionDate END) as [Location-18-Created], 
                MAX(CASE SubmissionLocation WHEN 18 THEN StationSubmissionBy END) as [Location-18-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 19 THEN StationSubmissionDate END) as [Location-19-Created], 
                MAX(CASE SubmissionLocation WHEN 19 THEN StationSubmissionBy END) as [Location-19-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 20 THEN StationSubmissionDate END) as [Location-20-Created], 
                MAX(CASE SubmissionLocation WHEN 20 THEN StationSubmissionBy END) as [Location-20-CreatedBy], 

                MAX(CASE SubmissionLocation WHEN 21 THEN StationSubmissionDate END) as [Location-21-Created], 
                MAX(CASE SubmissionLocation WHEN 21 THEN StationSubmissionBy END) as [Location-21-CreatedBy],

                MAX(CASE SubmissionLocation WHEN 62 THEN StationSubmissionDate END) as [Location-62-Created],
                MAX(CASE SubmissionLocation WHEN 62 THEN StationSubmissionBy END) as [Location-62-CreatedBy],

                MAX(CASE SubmissionLocation WHEN 47 THEN StationSubmissionDate END) as [Location-47-Created],
                MAX(CASE SubmissionLocation WHEN 47 THEN StationSubmissionBy END) as [Location-47-CreatedBy],

                MAX(CASE SubmissionLocation WHEN 63 THEN StationSubmissionDate END) as [Location-63-Created],
                MAX(CASE SubmissionLocation WHEN 63 THEN StationSubmissionBy END) as [Location-63-CreatedBy],

                MAX(CASE SubmissionLocation WHEN 11 THEN StationSubmissionDate END) as [Location-11-Created],
                MAX(CASE SubmissionLocation WHEN 11 THEN StationSubmissionBy END) as [Location-11-CreatedBy]

                FROM
                (
                    SELECT
                    inner_query.*,
                    stations.LocationID as SubmissionLocation,
                    MAX(stations.Created) as StationSubmissionDate,
                    stations.CreatedBy as StationSubmissionBy,
                    stations.MachineID
                    FROM
                    (
                        SELECT
                        a.AlignerID,
                        a.CaseID,
                        a.Step,
                        a.StepExtender,
                        a.Remake,
                        a.[Status],
                        STUFF((SELECT ',' + CAST(LotID as varchar(30)) FROM {{database}}.dbo.AlignerLotLinks WHERE AlignerID = a.AlignerID and BatchID = (SELECT MAX(BatchID) FROM {{database}}.dbo.AlignerLotLinks WHERE AlignerID = a.AlignerID) FOR XML PATH ('')), 1, 1, '') as LotNumber,
                        a.ProductID,
                        a.FixitID,
                        a.FixitCID,
                        a.Created,
                        STUFF((SELECT ',' + CAST(EmployeeID as varchar(30)) FROM {{database}}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID FOR XML PATH ('')), 1, 1, '') as CreatedID,
                        a.[Location] as CurrentLocation,
                        b.ID as LocationID
                        FROM
                        {{database}}.dbo.Aligners as a
                        OUTER APPLY 
                        (
                            SELECT 
                            ID, 
                            [Location] 
                            FROM 
                            {{database}}.dbo.Locations as b 
                            WHERE 
                            ID in (2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,24,34,35,36,37,62,47,63,11)
                        ) as b
                        {0}
                    ) as inner_query
                    OUTER APPLY 
                    (
                        SELECT 
                        a.*,
                        b.EmployeeID as CreatedBy
                        FROM 
                        {{database}}.dbo.Stations as a
                        OUTER APPLY (SELECT TOP 1 EmployeeID FROM {{database}}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b
                        WHERE 
                        AlignerID = inner_query.AlignerID 
                        and 
                        LocationID = inner_query.LocationID 
                        and 
                        [Status] = 11
                    ) as stations
                    GROUP BY
                    inner_query.AlignerID,
                    inner_query.CaseID,
                    inner_query.Step,
                    inner_query.StepExtender,
                    inner_query.Remake,
                    inner_query.Status,
                    inner_query.LotNumber,
                    inner_query.ProductID,
                    inner_query.FixitID,
                    inner_query.FixitCID,
                    inner_query.Created,
                    inner_query.CreatedID,
                    inner_query.CurrentLocation,
                    inner_query.LocationID,
                    stations.LocationID,
                    stations.CreatedBy,
                    stations.MachineID
                ) as source_table
                GROUP BY
                source_table.AlignerID,
                source_table.CaseID,
                source_table.Step,
                source_table.StepExtender,
                source_table.Remake,
                source_table.[Status],
                source_table.LotNumber,
                source_table.ProductID,
                source_table.FixitID,
                source_table.FixitCID,
                source_table.Created,
                source_table.CreatedID,
                source_table.CurrentLocation
            ) as aligners_table
            LEFT JOIN {{database}}.dbo.Cases as cases_table on cases_table.CaseID = aligners_table.CaseID
            OUTER APPLY (SELECT TOP 1 * FROM {{database}}.dbo.AlignerBagLinks WHERE aligners_table.AlignerID = AlignerID and Status = 11 ORDER BY ID DESC) as baglinks 
            OUTER APPLY (SELECT TOP 1 a.*, b.EmployeeID as CreatedID FROM {{database}}.dbo.Bags as a OUTER APPLY (SELECT TOP 1 EmployeeID FROM {{database}}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b WHERE baglinks.BagUDID = BagUDID ORDER BY Created DESC) as bags 
            OUTER APPLY (SELECT TOP 1 FDAProducts.* FROM {{database}}.dbo.FDAProducts LEFT JOIN {{database}}.dbo.CatalogProducts ON FDAProducts.ProductID = CatalogProducts.ProductID LEFT JOIN {{database}}.dbo.LabCustomerSettings	on CatalogProducts.[Catalog] = LabCustomerSettings.[Catalog] and LabCustomerSettings.CustomerID = cases_table.CustomerID WHERE aligners_table.ProductID = FDAProducts.ProductID	ORDER BY ID DESC) as fdaproduct 
            OUTER APPLY (SELECT TOP 1 * FROM {{database}}.dbo.Fixits WHERE aligners_table.FixitCID = FixitID ORDER BY FixitID DESC) as fixits
            {1}
        """
        # input: AlignerID
        # output: [[AlignerID, ...]]
        self.get_aligner_by_ID = self.aligners_template.format(
            "WHERE a.AlignerID = ?", "ORDER BY Step DESC"
        )
        # input: AlignerIDs
        # output: [[AlignerID, ...]]
        self.get_aligners_by_IDs = self.aligners_template.format(
            "WHERE a.AlignerID in (SELECT value FROM STRING_SPLIT(?, ','))",
            "ORDER BY Step DESC",
        )
        # input: CaseID
        # output: [[AlignerID, ...]]
        self.get_aligners_by_Case = self.aligners_template.format(
            "WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and CaseID = (SELECT TOP 1 CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?)",
            "ORDER BY Step DESC",
        )
        # input: CaseID, Step
        # output: [[AlignerID, ...]]
        self.get_aligners_by_CaseStep = self.aligners_template.format(
            "WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and CaseID = (SELECT TOP 1 CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?) and Step = ?",
            "ORDER BY Step DESC",
        )
        # input: CaseID, Step, Extender
        # output: [[AlignerID, ...]]
        self.get_aligners_by_CaseStepExt = self.aligners_template.format(
            "WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and CaseID = (SELECT TOP 1 CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?) and Step = ? and StepExtender = ?",
            "ORDER BY Step DESC",
        )
        self.get_aligners_by_CaseStepExtSimple = "SELECT a.AlignerID, a.Step, a.StepExtender FROM {database}.dbo.Aligners as a WHERE (SELECT CaseNumber FROM {database}.dbo.Cases WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) = ? and a.Step = ? and a.StepExtender = ?"
        # input: CaseID, Step, ProductID
        # output: [[AlignerID, ...]]
        self.get_aligners_by_CaseStepProduct = self.aligners_template.format(
            "WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and CaseID = (SELECT CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?) and Step = ? and ProductID = ?",
            "ORDER BY Step DESC",
        )
        # input: LocationID
        # output: [[AlignerID, ...]]
        self.get_aligners_by_loc = "SELECT a.AlignerID, b.CaseNumber, b.CustomerID, b.DueDate, a.CaseID, a.Step, a.StepExtender, a.Remake, a.Status, a.ProductID, a.FixitID, a.FixitCID, a.Location FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and a.Location = ? and b.Status = 'In Production' and b.Deleted = 0"
        # input: LocationID, CaseNumber
        # output: [[AlignerID, ...]]
        self.get_aligners_by_loc_by_case = "SELECT a.AlignerID, b.CaseNumber, b.CustomerID, b.DueDate, a.CaseID, a.Step, a.StepExtender, a.Remake, a.Status, a.ProductID, a.FixitID, a.FixitCID, a.Location FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and a.Location = ? and b.CaseNumber = ?"
        # input: AlignerID
        # output: [[AlignerID, ...]]
        self.get_remake_aligners_by_ID = "SELECT a.AlignerID, (SELECT CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, a.CaseID, a.Step, a.StepExtender, a.Remake, a.Status, a.ProductID, a.FixitID, a.FixitCID, a.Location FROM {database}.dbo.Aligners as a WHERE a.AlignerID = (SELECT Remake FROM {database}.dbo.Aligners WHERE AlignerID = ?) ORDER BY a.Step DESC"
        # input: AlignerID
        # output: [[AlignerID, ...]]
        self.get_remake_by_ID = ""
        # input: CaseID, Step, StepExtender
        # output: [[AlignerID, ...]]
        self.get_remake_by_casestep = ""
        # input: Status, StatusID, AlignerID
        # output: [[]]
        self.update_aligner_status = "UPDATE {database}.dbo.Aligners SET Status = ? OUTPUT Inserted.AlignerID WHERE AlignerID = ?"
        # input: FixitID, AlignerID
        # output: [[]]
        self.update_aligner_fixitid = "UPDATE {database}.dbo.Aligners SET FixitID = ? OUTPUT Inserted.AlignerID WHERE AlignerID = ?"
        # input: Product, ProductNID, AlignerID
        # output: [[]]
        self.update_aligner_product = "UPDATE {database}.dbo.Aligners SET ProductID = ? OUTPUT Inserted.AlignerID WHERE AlignerID = ?"
        self.insert_aligner_lot = "INSERT INTO {database}.dbo.AlignerLotLinks (AlignerID, LotID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, 11)"
        # input: LotNumber, LotNumberNID, AlignerID
        # output: [[]]
        self.update_aligner_lot = "UPDATE {database}.dbo.Aligners SET LotNumber = ? OUTPUT Inserted.AlignerID WHERE AlignerID = ?"
        # input: CaseID, Step, StepExtender, Status, ProductID, Priority, VerificationID
        # output: [[AlignerID]]
        self.insert_aligner_initial = "INSERT INTO {database}.dbo.Aligners (CaseID, Step, StepExtender, Status, ProductID, Priority, Created, VerificationID, OwnerVerificationID) OUTPUT Inserted.* VALUES (?, ?, ?, ?, ?, ?, GETDATE(), ?, ?)"
        # input: CaseID, Step, StepExtender, Remake, Status, ProductID, Priority, VerificationID
        # output: [[AlignerID]]
        self.insert_aligner_remake = "INSERT INTO {database}.dbo.Aligners (CaseID, Step, StepExtender, Remake, Status, ProductID, Priority, Created, VerificationID, fixitCID, OwnerVerificationID) OUTPUT Inserted.* VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, ?, ?)"
        # input: AlignerID, Location
        # output: [[Aligner]]
        self.get_alignerLocationHistory = "SELECT * FROM {{database}}.dbo.[Stations] WHERE AlignerID in ({0}) and LocationID in ({1}) and Status = 11"
        # input: CaseNumber, Step, AlignerID, Filename, ModelUUID, PartUUID
        # PrintedPartUUID, OrderUUID, PartOrderNumber, ApplicationID
        # VerificationID, Created, MachineID
        # output: [[CarbonID]]
        self.insert_Carbon = "INSERT INTO {database}.dbo.Carbon (CaseNumber, Step, AlignerID, Filename, ModelUUID, PartUUID, PrintedPartUUID, OrderUUID, PartOrderNumber, ApplicationID, VerificationID, Created, Status, MachineID, StationID) OUTPUT Inserted.CarbonID VALUES ((SELECT CaseNumber FROM {database}.dbo.Cases WHERE CaseID = (SELECT CaseID FROM {database}.dbo.Aligners WHERE AlignerID = ?)), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), 11, ?, ?)"
        # input: AligneriD
        # output: [[CaseNumber, Step, AlignerID, Filename, ModelUUID, PartUUID
        # PrintedPartUUID, OrderUUID, PartOrderNumber, ApplicationID
        # VerificationID, Created, MachineID]]
        self.get_Carbon = "SELECT * FROM {database}.dbo.Carbon WHERE AlignerID = ? and Status = 11 ORDER BY Created DESC"
        # input: CaseNumber
        # output: [[CaseNumber, Step, AlignerID, Filename, ModelUUID, PartUUID
        # PrintedPartUUID, OrderUUID, PartOrderNumber, ApplicationID
        # VerificationID, Created, MachineID]]
        self.get_Carbon_Case = "SELECT * FROM {database}.dbo.Carbon WHERE CaseNumber = ? and Status = 11 ORDER BY Created DESC"
        # input: ApplicationID, Offset, Rows
        # output: [[ID...]]
        self.get_aligners_in_Carbon = "SELECT CaseNumber, Filename, ModelUUID, PartUUID, PrintedPartUUID, OrderUUID, PartOrderNumber, VerificationID, Created, AlignerID, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as EmployeeID, Step FROM {database}.dbo.Carbon as a WHERE ApplicationID = ? and (DATEDIFF(SECOND, ?, Created) >= 0 and DATEDIFF(SECOND, ?, Created) <= 0) ORDER BY Created DESC OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        self.get_aligners_in_Carbon_by_filename = "SELECT CaseNumber, Filename, ModelUUID, PartUUID, PrintedPartUUID, OrderUUID, PartOrderNumber, VerificationID, Created, AlignerID, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as EmployeeID FROM {database}.dbo.Carbon WHERE CHARINDEX(?, Filename) = 1 and ApplicationID = ? ORDER BY Filename ASC"
        # input: AlignerID, CaseID, BagID
        # output: [[ID]]
        self.insert_Bag = "INSERT INTO {database}.dbo.Bagging (CaseID, AlignerID, Bagging, BaggingID, Status, MachineID) OUTPUT Inserted.ID VALUES ((SELECT CaseID FROM {database}.dbo.Aligners WHERE AlignerID = ?), ?, GETDATE(), ?, 11, ?)"
        # input: AlignerID
        # output: [[Aligner]]
        self.get_Bag = "SELECT * FROM {database}.dbo.Bagging WHERE AlignerID = ? and Status = 11 ORDER BY Bagging DESC"
        # input: AlignerID, LogTypeID, Change, VerificationID, Location
        # output: [[LogID]]
        self.insert_aligner_log = "INSERT INTO {database}.dbo.AlignerLog (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, Severity, AlignerID, CaseID, Created, VerificationID, Step, StepExtender, Remake, Status, ProductID, Priority, FixitID, FixitCID, Location) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, ?, (SELECT TOP 1 CaseID FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 Created FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 VerificationID FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 Step FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 StepExtender FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 Remake FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 Status FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 ProductID FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 Priority FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 FixitID FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 FixitCID FROM {database}.dbo.Aligners WHERE AlignerID = ?), (SELECT TOP 1 Location FROM {database}.dbo.Aligners WHERE AlignerID = ?))"
        # input: CaseNumber
        # output: [[AlignerID, LogTypeID, CaseID, Change, Date, VerificationID, Location]]
        self.get_aligner_log_by_case = "SELECT AlignerID, LogTypeID, CaseID, Change, LogNote, Logged, LoggedVerificationID, Step, StepExtender, Remake, Status, LotNumber, ProductID, Priority, FixitID, FixitCID, Path FROM {database}.dbo.AlignerLog WHERE CaseID = (SELECT CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?)"
        # input: AlignerID
        # output: [[AlignerID, LogTypeID, CaseID, Change, Date, VerificationID, Location]]
        self.get_aligner_log_by_aligner = "SELECT AlignerID, LogTypeID, CaseID, Change, LogNote, Logged, LoggedVerificationID, Step, StepExtender, Remake, Status, LotNumber, ProductID, Priority, FixitID, FixitCID, Path FROM {database}.dbo.AlignerLog WHERE AlignerID = ?"
        # input: AlignerID, BatchID
        # output: [[LinkID]]
        self.insert_aligner_batch_link = "INSERT INTO {database}.dbo.AlignerBatchLinks (AlignerID, BatchID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, 11)"
        # input: BatchID
        # output: [[AlignerID, Created]]
        self.get_aligners_by_batch = "SELECT a.AlignerID, (SELECT CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, a.CaseID, a.Step, a.StepExtender, a.Remake, a.Status, a.ProductID, a.FixitID, a.FixitCID, a.Location, b.Created as LinkCreated FROM {database}.dbo.Aligners as a, {database}.dbo.AlignerBatchLinks as b WHERE a.AlignerID = b.AlignerID and b.BatchID = ? and b.Status = 11 ORDER BY a.Step DESC"
        # input: Location
        # output: [[BatchID]]
        self.get_batches_by_location = "SELECT a.ID as BatchID, a.Created, c.EmployeeID as CreatedBy, a.VerificationID, a.Note, a.Location, a.Auxiliary, a.GaugeID, b.Percentage, b.Label FROM {database}.dbo.AlignerBatch as a OUTER APPLY (SELECT TOP 1 * FROM {database}.dbo.Gauges WHERE ID = a.GaugeID) as b OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as c WHERE a.Location = ? and (DATEDIFF(SECOND, ?, a.Created) >= 0 and DATEDIFF(SECOND, ?, a.Created) <= 0) ORDER BY a.Created DESC OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        # input: VerificationID
        # output: [[BatchID]]
        self.insert_aligner_batch = "INSERT INTO {database}.dbo.AlignerBatch (Created, VerificationID, Note, Location, GaugeID, Auxiliary) OUTPUT Inserted.ID VALUES (GETDATE(), ?, ?, ?, ?, ?)"
        # input: BatchID, Question, VerificationID
        # output: [[QuestionID]]
        self.insert_question = "INSERT INTO {database}.dbo.AlignerBatchQuestion (BatchID, Question, Response, Created, VerificationID) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?)"
        # input: BatchID
        # output: [[Qustion, VerificationID, Created]]
        self.get_question_by_batch = "SELECT Question, Response, Created, VerificationID FROM {database}.dbo.AlignerBatchQuestion WHERE BatchID = ?"
        # input: Location, AlignerID
        # output: AlignerID
        self.update_aligner_location = "UPDATE {database}.dbo.Aligners SET Location = ? OUTPUT Inserted.AlignerID WHERE AlignerID = ?"
        # input : AlignerID, FileTypeID
        # output: [[FileTypeID, Path, Created, VerificationID]]
        self.get_aligner_files = "SET NOCOUNT ON DROP TABLE IF EXISTS #TempFiles CREATE TABLE #TempFiles ( ID int, FileTypeID int, Path varchar(300), Created datetime, VerificationID varchar(50), Status int, OGAlignerID int ) DECLARE @Aligner as int SET @Aligner = ? WHILE @Aligner is not null BEGIN INSERT INTO #TempFiles (ID, FileTypeID, Path, Created, VerificationID, Status, OGAlignerID) (SELECT a.ID, b.FileTypeID, b.Path, a.Created, a.VerificationID, a.Status, @Aligner FROM {database}.dbo.AlignerFileLinks as a LEFT JOIN {database}.dbo.Files as b ON a.FileID = b.ID WHERE a.AlignerID = @Aligner and b.FileTypeID = ?) SET @Aligner = (SELECT Remake FROM {database}.dbo.Aligners WHERE AlignerID = @Aligner) END SELECT * FROM #TempFiles as a OUTER APPLY (SELECT TOP 1 EmployeeID as CreatedBy FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b ORDER BY Created DESC DROP TABLE #TempFiles"
        # input : AlignerID
        # output: [[FileID, Path, Created, VerificationID]]
        self.get_all_aligner_files = "SET NOCOUNT ON DROP TABLE IF EXISTS #TempFiles CREATE TABLE #TempFiles ( ID int, FileTypeID int, Path varchar(300), Created datetime, VerificationID varchar(50), Status int, OGAlignerID int ) DECLARE @Aligner as int SET @Aligner = ? WHILE @Aligner is not null BEGIN INSERT INTO #TempFiles (ID, FileTypeID, Path, Created, VerificationID, Status, OGAlignerID) (SELECT a.ID, b.FileTypeID, b.Path, a.Created, a.VerificationID, a.Status, @Aligner FROM {database}.dbo.AlignerFileLinks as a LEFT JOIN {database}.dbo.Files as b ON a.FileID = b.ID WHERE a.AlignerID = @Aligner) SET @Aligner = (SELECT Remake FROM {database}.dbo.Aligners WHERE AlignerID = @Aligner) END SELECT * FROM #TempFiles as a OUTER APPLY (SELECT TOP 1 EmployeeID as CreatedBy FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b ORDER BY Created DESC DROP TABLE #TempFiles"
        # input : AlignerID, FileTypeID
        # output: [[FileTypeID, Path, Created, VerificationID]]
        self.get_active_aligner_files = "SET NOCOUNT ON DROP TABLE IF EXISTS #TempFiles CREATE TABLE #TempFiles ( ID int, FileTypeID int, Path varchar(300), Created datetime, VerificationID varchar(50), Status int, OGAlignerID int ) DECLARE @Aligner as int SET @Aligner = ? WHILE @Aligner is not null BEGIN INSERT INTO #TempFiles (ID, FileTypeID, Path, Created, VerificationID, Status, OGAlignerID) (SELECT a.ID, b.FileTypeID, b.Path, a.Created, a.VerificationID, a.Status, @Aligner FROM {database}.dbo.AlignerFileLinks as a LEFT JOIN {database}.dbo.Files as b ON a.FileID = b.ID WHERE a.AlignerID = @Aligner and b.FileTypeID = ? and a.Status = 11) SET @Aligner = (SELECT Remake FROM {database}.dbo.Aligners WHERE AlignerID = @Aligner) END SELECT * FROM #TempFiles as a OUTER APPLY (SELECT TOP 1 EmployeeID as CreatedBy FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b ORDER BY Created DESC DROP TABLE #TempFiles"
        # input : AlignerID
        # output: [[FileTypeID, Path, Created, VerificationID]]
        self.get_all_active_aligner_files = "SET NOCOUNT ON DROP TABLE IF EXISTS #TempFiles CREATE TABLE #TempFiles ( ID int, FileTypeID int, Path varchar(300), Created datetime, VerificationID varchar(50), Status int, OGAlignerID int ) DECLARE @Aligner as int SET @Aligner = ? WHILE @Aligner is not null BEGIN INSERT INTO #TempFiles (ID, FileTypeID, Path, Created, VerificationID, Status, OGAlignerID) (SELECT a.ID, b.FileTypeID, b.Path, a.Created, a.VerificationID, a.Status, @Aligner FROM {database}.dbo.AlignerFileLinks as a LEFT JOIN {database}.dbo.Files as b ON a.FileID = b.ID WHERE a.AlignerID = @Aligner and Status = 11) SET @Aligner = (SELECT Remake FROM {database}.dbo.Aligners WHERE AlignerID = @Aligner) END SELECT * FROM #TempFiles as a OUTER APPLY (SELECT TOP 1 EmployeeID as CreatedBy FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b ORDER BY Created DESC DROP TABLE #TempFiles"
        # input: AlignerID, FileID, Path, VerificationID
        # output: [[ID]]
        self.insert_aligner_file = "INSERT INTO {database}.dbo.AlignerFileLinks (AlignerID, FileID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, ?)"
        # input: Status, ID
        # output: [[ID]]
        self.update_status_of_file = "UPDATE {database}.dbo.AlignerFileLinks SET Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        # input: ID
        # output: [[FileID, Path, Created, VerificationID]]
        self.get_aligner_files_by_linkID = "SELECT a.ID, b.FileTypeID, b.Path, a.Created, a.VerificationID, a.Status FROM {database}.dbo.AlignerFileLinks as a LEFT JOIN {database}.dbo.Files as b ON a.FileID = b.ID WHERE a.ID = ?"
        # input: plasticLotNumber
        # output: [[AlignerID, ...]]
        self.get_aligners_by_plastic_Lotnumber = "SELECT cases.CaseNumber, a.AlignerID, a.CaseID, a.Step, a.StepExtender, a.Remake, a.Status, a.ProductID, a.Priority, a.Created, a.VerificationID, a.FixitID, a.FixitCID, a.Path, a.Location FROM {database}.dbo.Aligners as a left join {database}.dbo.Cases as cases on a.CaseID = cases.CaseID left join {database}.dbo.AlignerLotLinks as lotlinks on a.AlignerID = lotlinks.AlignerID left join {database}.dbo.Lots as lots on lotlinks.LotID = lots.LotID left join {database}.dbo.Yields as yields on lots.YieldID = yields.YieldID left join {database}.dbo.Plastics as plastics on yields.plasticID = plastics.plasticID WHERE plastics.plasticLotNumber = ? ORDER BY cases.CaseNumber DESC"
        # input: LotNumber
        # output: [[AlignerID, ...]]
        self.get_aligners_by_Lot = "SELECT a.AlignerID, (SELECT CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, a.CaseID, a.Step, a.StepExtender, a.Remake, a.Status, a.ProductID, a.FixitID, a.FixitCID, a.Location FROM {database}.dbo.Aligners as a left join {database}.dbo.AlignerLotLinks as lotlinks on a.AlignerID = lotlinks.AlignerID WHERE lotlinks.LotID = ? ORDER BY a.Step DESC"
        # input: Location
        # output: [[AlignerID, CaseID, ...]]
        self.get_aligners_by_loc_fixit = "SELECT a.AlignerID, (SELECT CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, (SELECT CustomerID FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerID, (SELECT DueDate FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as DueDate, a.CaseID, a.Step, a.StepExtender, a.Remake, a.Status, a.ProductID, a.FixitID, a.FixitCID, a.Location FROM {database}.dbo.Aligners as a WHERE a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and a.Location = ? and a.FixitCID is not null and (SELECT Status FROM {database}.dbo.Fixits WHERE FixitID = a.FixitCID) = 2"
        self.get_aligners_by_loc_fixit_by_case = "SELECT a.AlignerID, (SELECT CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, (SELECT CustomerID FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerID, (SELECT DueDate FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as DueDate, a.CaseID, a.Step, a.StepExtender, a.Remake, a.Status, a.ProductID, a.FixitID, a.FixitCID, a.Location FROM {database}.dbo.Aligners as a WHERE a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and a.Location = ? and (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) = ? and a.FixitCID is not null and (SELECT Status FROM {database}.dbo.Fixits WHERE FixitID = a.FixitCID) = 2"
        # input: FixitID
        # output: [[AlignerID, CaseID, ...]]
        self.get_aligners_by_FixitID = self.aligners_template.format(
            "WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and FixitID = ?",
            "ORDER BY Step DESC",
        )
        # input: FixitID
        # output: [[AlignerID, CaseID, ...]]
        self.get_aligners_by_FixitCID = self.aligners_template.format(
            "WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and FixitCID = ?",
            "ORDER BY Step DESC",
        )
        # input: Date1, Date2
        # output: [[AlignerID, CaseID, ...]]
        self.get_aligners_by_Dates = self.aligners_template.format(
            "WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and DATEDIFF(day, ?, Created) >= 0 and DATEDIFF(day, ?, Created) <= 0 and Remake IS NULL",
            "ORDER BY Created, CaseNumber DESC OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY",
        )
        # input: AlignerID, VerificationID, LocationID, MachineID
        # output: [[StationID]]
        self.insert_Station = "INSERT INTO {database}.dbo.Stations (CaseID, AlignerID, Created, VerificationID, LocationID, Status, MachineID, FollowingLocationID) OUTPUT Inserted.ID VALUES ((SELECT CaseID FROM {database}.dbo.Aligners WHERE AlignerID = ?), ?, GETDATE(), ?, ?, 11, ?, ?)"
        # input: AlignerID
        # output: [[Aligner]]
        self.get_station_by_aligner = "SELECT a.ID, a.CaseID, a.AlignerID, a.Created, a.VerificationID, a.Status, a.LocationID, a.FollowingLocationID, a.MachineID, b.Label, b.Description, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CreatedBy FROM {database}.dbo.Stations as a left join {database}.dbo.Machines as b on a.MachineID = b.ID WHERE AlignerID = ? and Status = 11 ORDER BY Created DESC"
        # input: Status, Cases
        # output: [[Aligner]]
        self.get_aligners_by_string_list_cases = "SELECT a.AlignerID, (SELECT CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, a.CaseID, a.Step, a.StepExtender, a.Remake, a.Status, a.ProductID, a.FixitID, a.FixitCID, a.Location FROM {database}.dbo.Aligners as a WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) in (SELECT value FROM STRING_SPLIT(?, ',')) ORDER BY CaseNumber DESC"
        # input: Status, Aligner, n
        # output: [[Aligner]]
        self.get_aligner_by_aligner_and_location = "SELECT a.CaseID, a.AlignerID, a.Created, a.VerificationID, a.LocationID, a.Status, a.MachineID, a.FollowingLocationID FROM {database}.dbo.Stations as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and a.AlignerID = ? and a.LocationID = ?"
        self.get_aligner_by_aligner_and_location_fixit = ""
        # input: Date1, Date2
        # output: [[Aligner]]
        self.get_alignerQTY_by_Dates = "SELECT SUM(a.Quantity) as Quantity FROM {database}.dbo.CaseProducts as a join {database}.dbo.Cases as b on a.CaseID = b.CaseID WHERE b.[DateIn] >= ? AND b.[DateIn] <= ? AND b.[Status] IN ('In Production','Invoiced')"
        # input: CaseID, LocationID, startdate, enddate, offset, rows
        # output: [[Aligners]]
        self.get_station_aligners_by_Case_Location = "SELECT a.AlignerID, b.CaseNumber, a.CaseID, a.Created, a.VerificationID, a.LocationID, a.FollowingLocationID, a.Status FROM {database}.dbo.Stations as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and a.LocationID = ? and b.Deleted = 0 and b.CaseNumber = ? and (DATEDIFF(SECOND, ?, a.Created) >= 0 and DATEDIFF(SECOND, ?, a.Created) <= 0) ORDER BY Created DESC OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"

        self.get_location_history_by_date_range = "SELECT a.ID, a.AlignerID, a.Created, a.VerificationID, a.Status, (SELECT CaseNumber FROM {database}.dbo.Cases WHERE CaseID = c.CaseID) as CaseNumber, b.*, c.Step FROM {database}.dbo.AlignerBatchLinks as a left join {database}.dbo.Aligners as c on a.AlignerID = c.AlignerID left join ( SELECT a.ID as BatchID, a.Created as BatchCreated, a.VerificationID as BatchCreatedBy, a.Location, a.Note, b.ID as GaugeID, b.Title, b.Label, b.Limit, b.[Index], b.Length, b.Constant, b.Percentage, b.Status as GaugeStatus, b.Created as GaugeCreated, b.VerificationID as GaugeCreatedBy, b.LockID FROM {database}.dbo.AlignerBatch as a Outer apply (SELECT * FROM {database}.dbo.Gauges where ID = a.GaugeID) as b) as b on a.BatchID = b.BatchID WHERE b.[Location] = ? and (DATEDIFF(SECOND, ?, b.BatchCreated) >= 0 and DATEDIFF(SECOND, ?, b.BatchCreated) <= 0) order by a.Created desc OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        # input: Status, LocationID
        # output: [[Aligners]]
        self.get_station_aligners_by_Location = "SELECT a.AlignerID, b.CaseNumber, a.CaseID, a.Created, a.VerificationID, a.LocationID, a.FollowingLocationID, a.Status FROM {database}.dbo.Stations as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and a.LocationID = ? and b.Deleted = 0 and (DATEDIFF(SECOND, ?, a.Created) >= 0 and DATEDIFF(SECOND, ?, a.Created) <= 0) ORDER BY Created DESC OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        # input: LocationID, startdate, enddate, offset, rows
        # input: Status, StartDate, EndDate
        # output: [[Aligners]]
        self.get_aligners_by_Date_range = self.aligners_template.format(
            "WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and DATEDIFF(day, ?, Created) >= 0 and DATEDIFF(day, ?, Created) <= 0 and Remake IS NOT NULL",
            "ORDER BY Created, CaseNumber DESC",
        )
        # input: Location, StartDate, EndDate, Offset, Rows
        # output: [[Aligners]]
        self.get_location_history_by_date_range = "SELECT a.ID, a.AlignerID, a.Created, a.VerificationID, a.Status, (SELECT CaseNumber FROM {database}.dbo.Cases WHERE CaseID = c.CaseID) as CaseNumber, b.*, c.Step FROM {database}.dbo.AlignerBatchLinks as a left join {database}.dbo.Aligners as c on a.AlignerID = c.AlignerID left join ( SELECT a.ID as BatchID, a.Created as BatchCreated, a.VerificationID as BatchCreatedBy, a.Location, a.Note, b.ID as GaugeID, b.Title, b.Label, b.Limit, b.[Index], b.Length, b.Constant, b.Percentage, b.Status as GaugeStatus, b.Created as GaugeCreated, b.VerificationID as GaugeCreatedBy, b.LockID FROM {database}.dbo.AlignerBatch as a Outer apply (SELECT * FROM {database}.dbo.Gauges where ID = a.GaugeID) as b) as b on a.BatchID = b.BatchID WHERE b.[Location] = ? and (DATEDIFF(SECOND, ?, b.BatchCreated) >= 0 and DATEDIFF(SECOND, ?, b.BatchCreated) <= 0) order by a.Created desc OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        self.transfer_aligners = "UPDATE {database}.dbo.Aligners SET CaseID = (SELECT TOP 1 CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?) OUTPUT Inserted.AlignerID WHERE AlignerID = ?"
        # input: AlignerID, AlignerID, ...
        # output [[Step, Step, ...]]
        self.get_steps_from_alignerIDs = "SELECT Step FROM {database}.dbo.Aligners WHERE AlignerID in (SELECT value FROM STRING_SPLIT(?, ','))"

        aligner_lot_link_query = "SELECT AlignerLotLinksTable.*, LotsTable.YieldID, LotsTable.BinID, LotsTable.DateIn, LotsTable.DateOut, LotsTable.CheckInVerificationID, LotsTable.CheckOutVerificationID, AlignersTable.CaseID, AlignersTable.Step, AlignersTable.StepExtender, AlignersTable.Remake, AlignersTable.Status, AlignersTable.ProductID, AlignersTable.Priority, AlignersTable.Created as AlignerCreated, AlignersTable.VerificationID as AlignerVerificationID, AlignersTable.FixitID, AlignersTable.FixitCID, AlignersTable.Location FROM {database}.dbo.AlignerLotLinks as AlignerLotLinksTable LEFT JOIN {database}.[dbo].[Aligners] AlignersTable ON AlignerLotLinksTable.AlignerID = AlignersTable.AlignerID LEFT JOIN {database}.[dbo].[Lots] LotsTable ON AlignerLotLinksTable.LotID = LotsTable.LotID"
        # output: list of links
        self.get_aligner_lot_links = (
            aligner_lot_link_query + " WHERE AlignerLotLinksTable.Status = 11"
        )
        # input: AlignerLotLinkID
        # output: list of links
        self.get_aligner_lot_links_by_link = (
            aligner_lot_link_query
            + " WHERE AlignerLotLinksTable.Status = 11 AND AlignerLotLinksTable.ID = ?"
        )
        # input: AlignerID
        # output: list of links
        self.get_aligner_lot_links_by_aligner = (
            aligner_lot_link_query
            + " WHERE AlignerLotLinksTable.Status = 11 AND AlignerLotLinksTable.AlignerID = ?"
        )
        # input: LotID
        # output: list of links
        self.get_aligner_lot_links_by_lot = (
            aligner_lot_link_query
            + " WHERE AlignerLotLinksTable.Status = 11 AND AlignerLotLinksTable.LotID = ?"
        )
        # input: VerificationID
        # output: AlignerLotBatch ID
        self.insert_aligner_lot_batch = "INSERT INTO {database}.dbo.AlignerLotBatch (Created, VerificationID, GaugeID, Status) OUTPUT Inserted.ID VALUES (GETDATE(), ?, ?, 11)"
        # input: AlignerID, VerificationID, LotIDs as "1,2,3"
        # output: list AlignerLotLink ID
        self.insert_aligner_lot_links = "INSERT INTO {database}.dbo.AlignerLotLinks (BatchID, AlignerID, LotID, Created, VerificationID, Status) OUTPUT Inserted.ID as LinkID SELECT ?, ?, value, GETDATE(), ?, 11 FROM STRING_SPLIT(?, ',')"
        # input: LotID, AlignerLotLink ID
        # output: AlignerLotLink ID
        self.update_aligner_lot_links_lotID = "UPDATE {database}.dbo.AlignerLotLinks SET LotID = ? OUTPUT Inserted.ID WHERE ID = ?"
        # input: Status, AlignerLotLink ID
        # output: AlignerLotLink ID
        self.update_aligner_lot_links_status = "UPDATE {database}.dbo.AlignerLotLinks SET Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        # input: AlignerID
        # output: StationID
        self.update_aligner_station_status = "UPDATE {database}.dbo.Stations SET Status = ? OUTPUT Inserted.ID WHERE AlignerID in (SELECT value FROM STRING_SPLIT(?, ','))"
        # input: AlignerID
        # output: AlignerFileLinkID
        self.update_aligner_filelink_status = "UPDATE {database}.dbo.AlignerFileLinks SET Status = ? OUTPUT Inserted.ID FROM {database}.dbo.AlignerFileLinks as filelinks LEFT JOIN {database}.dbo.Files as files on filelinks.FileID = files.ID WHERE filelinks.AlignerID in (SELECT value FROM STRING_SPLIT(?, ',')) and files.FileTypeID in (SELECT value FROM STRING_SPLIT(?, ','))"
