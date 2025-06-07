import generalManger.generalManger as gm
import data.constants as dc

dc.StartupConsts.WITH_TRACKING = True
# not used at the moment. TODO: change the startup ETR defaults when DEBUG
dc.StartupConsts.DEBUG = False

gm.GeneralManger.StartApp()