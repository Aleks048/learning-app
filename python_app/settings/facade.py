import settings.settings as s
import settings.manager as sm


class Wr:
    class Manager(sm.Manager):
        pass

    class Data:
        class TokenIDs:
            class AppIds(s.IdTokens.Apps):
                pass
            
            class Misc(s.IdTokens.Misc):
                pass