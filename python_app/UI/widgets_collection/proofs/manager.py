import UI.widgets_collection.proofs.proofs as prw

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils._utils_main as _u


class LayoutManagers:

    class ProofsLayout(wm.MenuLayout_Interface):
        prefix = "_ExcerciseLayout_"

        def __init__(self, winRoot):
            appDimensions = [720, 800]
            super().__init__(winRoot.frame, appDimensions)
            self.proofMainImage = prw.EntryImages_BOX(winRoot.frame, self.prefix)
            self.addWidget(self.proofMainImage)
            self.proof_BOX = prw.Proof_BOX(winRoot.frame, self.prefix)
            self.addWidget(self.proof_BOX)
            # self.moveTOCtoProofEntry_BTN = prw.MoveTOCtoProofEntry_BTN(winRoot.frame, self.prefix)
            # self.addWidget(self.moveTOCtoProofEntry_BTN)

            winRoot.setGeometry(*self.appDimensions)

            self.winRoot = winRoot
        def show(self):
            self.proofMainImage.subsection = self.winRoot.subsection
            self.proofMainImage.imIdx = self.winRoot.imIdx

            # self.moveTOCtoProofEntry_BTN.subsection = self.winRoot.subsection
            # self.moveTOCtoProofEntry_BTN.imIdx = self.winRoot.imIdx

            self.proof_BOX.subsection = self.winRoot.subsection
            self.proof_BOX.imIdx = self.winRoot.imIdx

            super().show()

            # resize the solution box in respect to the size of the main image
            self.proofMainImage.update()
            self.proof_BOX.setCanvasHeight(800 - 20 - self.proofMainImage.getHeight())
            self.proof_BOX.update()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class ProofsManager(wm.MenuManager_Interface):
    def __init__(self):
        self.__winRoots = {}
        
        super().__init__(None,
                        None,
                        None)

    def __addWinRoot(self, subsection, imIdx):
        winRoot = prw.ProofsRoot(width = 50, 
                                 height = 50, 
                                 subsection = subsection,
                                 imIdx = str(imIdx)
                                 )
        layout = LayoutManagers.listOfLayouts()[0](winRoot)
        winRoot.changeTitle(f"proofs for {subsection} {imIdx}")
        self.__winRoots[str(subsection) + str(imIdx)] = layout

    def show(self, subsection, imIdx):
        if self.__winRoots.get(str(subsection) + str(imIdx)) == None:
            self.__addWinRoot(subsection, imIdx)

        layout = self.__winRoots.get(str(subsection) + str(imIdx))
        layout.winRoot.render()
        layout.winRoot.forceFocus()
        layout.show()

    def hideAll(self):
        for _, v in self.__winRoots.items():
            v.hide()
            v.winRoot.destroy()

    def hide(self):
        self.hideAll()

    def hide(self, subsection, imIdx):
        layout = self.__winRoots.pop(str(subsection) + str(imIdx))
        layout.hide()
        layout.winRoot.destroy()
    
    def refresh(self, subsection, imIdx):
        if self.__winRoots.get(str(subsection) + str(imIdx)) != None:
            self.hide(subsection, imIdx)
            self.show(subsection, imIdx)
