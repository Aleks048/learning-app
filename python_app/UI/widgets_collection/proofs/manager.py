import UI.widgets_collection.proofs.proofs as prw

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils._utils_main as _u


class LayoutManagers:

    class ProofsLayout(wm.MenuLayout_Interface):
        prefix = "_ExcerciseLayout_"
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t

        def __init__(self, winRoot):
            appDimensions = [720, 800, 0, 0]
            super().__init__(winRoot, appDimensions)
            self.proofMainImage = prw.ProofMainImage(winRoot, self.prefix)
            self.addWidget(self.proofMainImage)
            self.proof_BOX = prw.Proof_BOX(winRoot, self.prefix)
            self.addWidget(self.proof_BOX)
            self.hideProofsWindow_BTN = prw.HideProofsWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.hideProofsWindow_BTN)
            self.moveTOCtoProofEntry_BTN = prw.MoveTOCtoProofEntry_BTN(winRoot, self.prefix)
            self.addWidget(self.moveTOCtoProofEntry_BTN)

            winRoot.setGeometry(*self.appDimensions)
        def show(self):
            self.proofMainImage.subsection = self.subsection
            self.proofMainImage.entryIdx = self.imIdx


            self.hideProofsWindow_BTN.subsection = self.subsection
            self.hideProofsWindow_BTN.imIdx = self.imIdx

            self.moveTOCtoProofEntry_BTN.subsection = self.subsection
            self.moveTOCtoProofEntry_BTN.imIdx = self.imIdx

            self.proof_BOX.subsection = self.subsection
            self.proof_BOX.imIdx = self.imIdx

            super().show()

            # resize the solution box in respect to the size of the main image
            self.proofMainImage.widgetObj.update()
            self.proof_BOX.canvas.configure(height = 730 - 20 - self.proofMainImage.widgetObj.winfo_height())
            self.proof_BOX.canvas.update()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class ProofsManager(wm.MenuManager_Interface):
    imIdx = 0
    def __init__(self):

        winRoot = prw.ProofsRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
    def show(self):
        self.layouts[0].subsection = self.subsection
        self.layouts[0].imIdx = self.imIdx
        return super().show()
