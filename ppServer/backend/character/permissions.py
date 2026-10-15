import enum

class CustomPermission(enum.Enum):
    """ not used in templates in favor of easier, literal 'perms.character.is_Spielleitung', ... """

    SPIELLEITUNG = "character.is_Spielleitung"
    LARP = "character.is_LARPler"
    COPY_CHARS = "character.copies_chars"
    SEES_CALENDAR = "character.sees_TODOcalendar"