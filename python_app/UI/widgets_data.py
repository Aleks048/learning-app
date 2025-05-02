class Data:
    class ENT:
        entryWidget_ID = "ETR"

        regularTextColor = "white"
        defaultTextColor = "blue"
    class BTN:
        buttonWidget_ID = "BTN"
    
    class ExcerciseLayout:
        small = -150
        normal = 0
        large = 150

        currSize = normal

    class ProofsLayout:
        small = -150
        normal = 0
        large = 150

        currSize = normal

    class MainEntryLayout:
        no = None
        small = -300
        normal = 0
        large = 300

        currSize = normal

        largeLinks = False
        largeLinksSize = 600
        regularLinksSize = 300

    class General:
        singleSubsection = True

    class Reactors:
        entryChangeReactors = {}
        subsectionChangeReactors = {}
        excerciseLineChangeReactors = {}
