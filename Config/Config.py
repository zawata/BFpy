from enum import Enum

# Left Cells             = Unbounded (0-Indexed)
# Right Cells            = Unbounded (0-Indexed)
# Cell Size              = 8         (bytes)
# NewLine                = 0x10
# Right Bracket Check    = True
# EOC                    = !
# Comments               = #Comment#
# Invalid Characters     = warn
# Spaces, tabs, newlines = allowed

class Right_Bracket_Behavior_Enum(Enum):
    CONDITIONAL   = 0,
    UNCONDITIONAL = 1

class End_of_Tape_Behavior_Enum(Enum):
    DONT_MOVE   = 0,
    WRAP_AROUND = 1,
    CRASH       = 2

class End_of_File_Behavior_Enum(Enum):
    UNCHANGED = 0,
    ZERO      = 1,
    C_STYLE   = 2

class Config:
    Debug_Flag             = False
    Buffered_Output_Flag   = False
    Realtime_Input_Flag    = False

    Left_Cell_Limit        = -1
    Right_Cell_Limit       = -1
    Cell_Size              = -1
    End_of_Tape_Behavior   = End_of_Tape_Behavior_Enum.DONT_MOVE
    Right_Bracket_Behavior = Right_Bracket_Behavior_Enum.CONDITIONAL


