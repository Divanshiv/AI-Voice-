import json
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai
from app.config import get_settings
from app.models.chat_models import ProductInfo, MenuOption


SCRIPT = {
    "en": {
        "greeting": "Hello! I'm your AI Voice Assistant. I can help you learn about our products, answer questions, or guide you through our services. What would you like to do today?",
        "menu": "Here are our categories:\n1. Mobiles - Samsung, Vivo, Oppo, Other Brands\n2. Watches - Smart Watches, Analog Watches\n3. Shirts - Printed Shirts, Plain Shirts\n4. T-Shirts - Printed, Oversized, Plain\n\nWhat would you like to shop for?",
        "select_brand": "You selected {category}! Please select a brand:",
        "products": "Here are {brand} products:\n{products}\nAny product you'd like more details on?",
        "not_understood": "Sorry, I didn't understand that. Did you mean Mobiles, Watches, Shirts, or T-Shirts? Or say 'menu' to see all options.",
        "nice_choice": "Nice choice! That's a popular category.",
        "exit": "Thank you for shopping with us! Have a great day!"
    },
    "hi": {
        "greeting": "नमस्ते! मैं आपका AI Voice Assistant हूं। मैं आपको products के बारे में बता सकता हूं, सवालों के जवाब दे सकता हूं, या services में मार्गदर्शन कर सकता हूं। आज आप क्या करना चाहेंगे?",
        "menu": "हमारे categories:\n1. Mobiles - Samsung, Vivo, Oppo, Other Brands\n2. Watches - Smart Watches, Analog Watches\n3. Shirts - Printed Shirts, Plain Shirts\n4. T-Shirts - Printed, Oversized, Plain\n\nआप क्या खरीदना चाहेंगे?",
        "select_brand": "आपने {category} select किया! कृपया brand select करें:",
        "products": "यहां {brand} products हैं:\n{products}\nक्या किसी product के बारे में और जानना चाहेंगे?",
        "not_understood": "माफ कीजिए, मुझे समझ नहीं आया। क्या आपका मतलब Mobiles, Watches, Shirts, या T-Shirts से है? या 'menu' बोलें।",
        "nice_choice": "बहुत अच्छी choice! यह popular category है।",
        "exit": "हमारे साथ खरीदारी के लिए धन्यवाद! आपका दिन शुभ हो!"
    }
}

CATEGORY_KEYWORDS = {
    "mobiles": ["mobiles", "mobile", "phone", "phones", "smartphone", "iphone", "android"],
    "watches": ["watches", "watch", "smartwatch", "analog"],
    "shirts": ["shirts", "shirt", "formal shirt", "casual shirt"],
    "tshirts": ["tshirts", "tshirt", "t-shirt", "t shirt", "tee"]
}


class AIService:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            
        self.product_info = self._load_product_info()
        self.chat_sessions = {}
        self.user_sessions = {}
    
    def _load_product_info(self) -> ProductInfo:
        product_file = Path(__file__).parent.parent.parent / "product_info.json"
        with open(product_file, 'r') as f:
            data = json.load(f)
        return ProductInfo(
            name=data.get("name", ""),
            tagline=data.get("tagline", ""),
            description=data.get("description", ""),
            products=data,
            company=data.get("company", {}),
            greeting=data.get("greeting", {}),
            menu_options=[]
        )
    
    def _init_user_session(self, session_id: str):
        self.user_sessions[session_id] = {
            "state": "greeting",
            "category": None,
            "subcategory": None
        }
    
    def _get_user_state(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.user_sessions:
            self._init_user_session(session_id)
        return self.user_sessions[session_id]
    
    def _update_user_state(self, session_id: str, **kwargs):
        state = self._get_user_state(session_id)
        state.update(kwargs)
        self.user_sessions[session_id] = state
    
    def _find_category(self, user_input: str) -> str:
        user_lower = user_input.lower()
        for cat_id, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in user_lower:
                    return cat_id
        return None
    
    def _format_products(self, category_id: str, subcategory_id: str) -> str:
        data = self.product_info.products
        categories = data.get("categories", [])
        category = next((c for c in categories if c.get("id") == category_id), None)
        if not category:
            return ""
        subcategory = next((s for s in category.get("subcategories", []) if s.get("id") == subcategory_id), None)
        if not subcategory:
            return ""
        
        products = subcategory.get("products", [])
        text = ""
        for p in products:
            text += f"• {p.get('name')} - {p.get('price')}\n  {p.get('description')}\n  Features: {', '.join(p.get('features', []))}\n\n"
        return text
    
    def _get_categories_menu(self) -> List[MenuOption]:
        data = self.product_info.products
        categories = data.get("categories", [])
        options = []
        for cat in categories:
            options.append(MenuOption(
                id=cat.get("id"),
                label=f"{cat.get('emoji', '')} {cat.get('name', '')}",
                description=f"Browse {cat.get('name', '')}",
                prompt=f"show {cat.get('name', '')}"
            ))
        return options
    
    def get_greeting(self, language: str = "en") -> str:
        return SCRIPT.get(language, SCRIPT["en"])["greeting"]
    
    def get_menu_options(self) -> List[MenuOption]:
        return self._get_categories_menu()
    
    def get_product_info_text(self, language: str = "en") -> str:
        return SCRIPT.get(language, SCRIPT["en"])["menu"]
    
    def generate_response(self, user_message: str, session_id: str, language: str = "en") -> tuple:
        user_state = self._get_user_state(session_id)
        user_input = user_message.strip().lower()
        msg_original = user_message.strip()
        script = SCRIPT.get(language, SCRIPT["en"])
        
        if user_input in ["menu", "back", "start over", "show menu", "सभी देखो"]:
            self._init_user_session(session_id)
            return script["menu"], self._get_categories_menu()
        
        if user_input in ["exit", "goodbye", "bye", "quit", "thank you", "thanks", "बाहर", "अलविदा"]:
            return script["exit"], []
        
        if user_input in ["hello", "hi", "hey", "नमस्ते", "नमस्कार", "hola"]:
            return script["greeting"], self._get_categories_menu()
        
        if user_input in ["nice choice", "great", "cool", "awesome"]:
            return script["nice_choice"], self._get_categories_menu()
        
        if user_input in ["what is shopping", "tell me about shopping", "shopping kya hai"]:
            if language == "hi":
                "Shopping का मतलब है products खरीदना! हमारे पास Mobiles, Watches, Shirts, और T-Shirts हैं। क्या खरीदना चाहेंगे?"
            return "Shopping means buying products! We have Mobiles, Watches, Shirts, and T-Shirts. What would you like to buy?", self._get_categories_menu()
        
        current_state = user_state.get("state", "greeting")
        
        if current_state == "products" and user_state.get("subcategory"):
            cat_id = user_state.get("category")
            sub_id = user_state.get("subcategory")
            products_text = self._format_products(cat_id, sub_id)
            
            data = self.product_info.products
            categories = data.get("categories", [])
            category = next((c for c in categories if c.get("id") == cat_id), None)
            subcategory = next((s for s in category.get("subcategories", []) if s.get("id") == sub_id), None) if category else None
            
            return script["products"].format(brand=subcategory.get("name") if subcategory else "", products=products_text), []
        
        if current_state == "subcategory" and user_state.get("category"):
            cat_id = user_state.get("category")
            data = self.product_info.products
            categories = data.get("categories", [])
            category = next((c for c in categories if c.get("id") == cat_id), None)
            
            if category:
                subcategories = category.get("subcategories", [])
                for i, sub in enumerate(subcategories, 1):
                    sub_name = sub.get("name", "").lower()
                    if str(i) in user_input or sub_name in user_input or sub.get("id") in user_input:
                        self._update_user_state(session_id, state="products", subcategory=sub.get("id"))
                        products_text = self._format_products(cat_id, sub.get("id"))
                        return script["products"].format(brand=sub.get("name"), products=products_text), []
            
            return script["not_understood"], self._get_categories_menu()
        
        if current_state in ["greeting", "category"]:
            cat_id = self._find_category(user_input)
            
            if cat_id:
                self._update_user_state(session_id, state="subcategory", category=cat_id)
                data = self.product_info.products
                categories = data.get("categories", [])
                category = next((c for c in categories if c.get("id") == cat_id), None)
                return script["select_brand"].format(category=category.get("name")), self._get_categories_menu()
            
            if not self.api_key or not self.model:
                return "Demo mode! Say 'mobiles', 'watches', 'shirts', or 't-shirts' to browse products.", []
            
            try:
                chat = self.chat_sessions.get(session_id)
                
                system_prompt = f"""You are ShopEasy - a friendly shopping voice assistant.
Be conversational and helpful. Keep responses SHORT.
Match user intent:
- If they ask about shopping definition -> explain we sell products
- If they mention any category (mobiles/watches/shirts/tshirts) -> go to that category
- If unclear -> show categories

Categories to offer: Mobiles, Watches, Shirts, T-Shirts
Always be friendly, short, and offer help."""

                greeting_text = script["greeting"]
                
                if not chat:
                    chat = self.model.start_chat(history=[
                        {"role": "user", "parts": [system_prompt]},
                        {"role": "model", "parts": [greeting_text]}
                    ])
                    self.chat_sessions[session_id] = chat
                
                response = chat.send_message(msg_original)
                response_text = response.text
                
                for cat_id, keywords in CATEGORY_KEYWORDS.items():
                    for kw in keywords:
                        if kw in response_text.lower():
                            self._update_user_state(session_id, state="subcategory", category=cat_id)
                            data_new = self.product_info.products
                            categories = data_new.get("categories", [])
                            category = next((c for c in categories if c.get("id") == cat_id), None)
                            if category:
                                return script["select_brand"].format(category=category.get("name")), self._get_categories_menu()
                
                return response_text, self._get_categories_menu()
                
            except Exception as e:
                print(f"AI Error: {e}")
                return script["menu"], self._get_categories_menu()
        
        return script["menu"], self._get_categories_menu()
    
    def clear_session(self, session_id: str):
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]


ai_service = AIService()