from fastcoref import spacy_component
import spacy


class CorefResolver:
    def __init__(self, model_path = None, ):
        
        if model_path:
           self.nlp_model = spacy.load(model_path)
        else:
           print("No model_path provided, loading default spacy model...")
           self.nlp_model = spacy.load("en_core_web_sm")

        self.nlp_model.add_pipe("fastcoref")


    def resolve_corefs_text(self, in_text):
        
        nlp_pipeline = self.nlp_model(
                            in_text, 
                            component_cfg={"fastcoref": {'resolve_text': True}}
        )
        resolved_coref_text = nlp_pipeline._.resolved_text

        return resolved_coref_text