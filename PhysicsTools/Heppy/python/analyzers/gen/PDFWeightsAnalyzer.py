from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
import PhysicsTools.HeppyCore.framework.config as cfg
from DataFormats.FWLite import Handle, Runs #MF LHE

        
class PDFWeightsAnalyzer( Analyzer ):
    """    """
    def __init__(self, cfg_ana, cfg_comp, looperName ):
        super(PDFWeightsAnalyzer,self).__init__(cfg_ana,cfg_comp,looperName)
        self.doPDFWeights = hasattr(self.cfg_ana, "PDFWeights") and len(self.cfg_ana.PDFWeights) > 0
        self.doPDFVars = hasattr(self.cfg_ana, "doPDFVars") and self.cfg_ana.doPDFVars == True
        if hasattr(self.cfg_ana, "PDFGen"):
            self.PDFGen = self.cfg_ana.PDFGen
        else:
            self.PDFGen = "MG"
        if self.doPDFWeights:
            self.pdfWeightInit = False
    #---------------------------------------------
    # DECLARATION OF HANDLES OF GEN LEVEL OBJECTS 
    #---------------------------------------------
        

    def declareHandles(self):
        super(PDFWeightsAnalyzer, self).declareHandles()

        if self.doPDFVars or self.doPDFWeights:
            self.mchandles['pdfstuff'] = AutoHandle( 'generator', 'GenEventInfoProduct' )
            self.mchandles['EvtHandle'] = AutoHandle( 'externalLHEProducer', 'LHEEventProduct' ) #MF LHE
#            self.runHandle = Handle('LHERunInfoProduct') #MF LHE
#            self.run = Runs('root://eoscms.cern.ch//eos/cms/store/mc/RunIIFall15MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/70000/002ABFCA-A0B9-E511-B9BA-0CC47A57CD6A.root') #MF LHE
            self.run = Runs(self.cfg_comp.files[0]) #MF LHE
#            self.run.getByLabel( 'externalLHEProducer', self.runHandle ) #MF LHE

    def beginLoop(self, setup):
        super(PDFWeightsAnalyzer,self).beginLoop(setup)

    def initPDFWeights(self):
        print "PDFGen: %s" % self.PDFGen
        from ROOT import PdfWeightProducerTool
        self.pdfWeightInit = True
        self.pdfWeightTool = PdfWeightProducerTool()
        for pdf in self.cfg_ana.PDFWeights:
            self.pdfWeightTool.addPdfSet(pdf+".LHgrid")
        self.pdfWeightTool.beginJob() #MF LHE
#        self.pdfWeightTool.beginJob(self.runHandle.product()) #MF LHE

    def makePDFWeights(self, event):
        if not self.pdfWeightInit: self.initPDFWeights()
        self.pdfWeightTool.processEvent(self.genInfo)
        event.pdfWeights = {}
        for pdf in self.cfg_ana.PDFWeights:
            ws = self.pdfWeightTool.getWeights(pdf+".LHgrid")
            event.pdfWeights[pdf] = [w for w in ws]
        #from MINIAOD
        self.pdfWeightTool.extractWeight(self.mchandles['pdfstuff'].product() ,  self.mchandles['EvtHandle'].product()) #MF LHE
        event.exWeight_pdf = {} #MF LHE
        ws = self.pdfWeightTool.getExWeights( self.PDFGen , "pdf" ) #for MadGraph samples #MF LHE
        event.exWeight_pdf = [w for w in ws] #MF LHE
        event.exWeight_scale = {} #MF LHE
        ws = self.pdfWeightTool.getExWeights( self.PDFGen , "scale" ) #for MadGraph samples #MF LHE
        event.exWeight_scale = [w for w in ws] #MF LHE
        event.exWeight_as = {} #MF LHE
        ws = self.pdfWeightTool.getExWeights( self.PDFGen , "as" ) #for MadGraph samples #MF LHE
        event.exWeight_as = [w for w in ws] #MF LHE

    def process(self, event):
        self.readCollections( event.input )

        # if not MC, nothing to do
        if not self.cfg_comp.isMC: 
            return True

        if self.doPDFVars or self.doPDFWeights:
            self.genInfo = self.mchandles['pdfstuff'].product()
        if self.doPDFWeights:
            self.makePDFWeights(event)
        if self.doPDFVars:
            event.pdf_x1 = self.genInfo.pdf().x.first
            event.pdf_x2 = self.genInfo.pdf().x.second
            event.pdf_id1 = self.genInfo.pdf().id.first
            event.pdf_id2 = self.genInfo.pdf().id.second
            event.pdf_scale = self.genInfo.pdf().scalePDF

        return True

setattr(PDFWeightsAnalyzer,"defaultConfig",
    cfg.Analyzer(PDFWeightsAnalyzer,
        PDFWeights = []
    )
)
