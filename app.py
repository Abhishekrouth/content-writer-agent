from flask import Flask, request, jsonify
from flask_cors import CORS
import webview
import pyperclip
import keyboard
import threading
import queue
import time
import os
import ctypes
import json
from processor import Processor
from routes import GENERATE_NEW_LINE_API, GRAMMAR_CHECK_API, ALTERNATIVE_API, TRANSLATING_API

app = Flask(__name__)
CORS(app)

global_app_instance = None

def get_selected_text():
    pyperclip.copy('') 
    keyboard.send('ctrl+c')
    time.sleep(0.1) 
    text = pyperclip.paste()
    return text


@app.route(GRAMMAR_CHECK_API, methods=["POST"])
def grammar():
    
    if not global_app_instance: return jsonify({"error": "App not ready"}), 500
        
    data = request.json
    text = data.get('text', '')
    context = data.get('context', '')
    language = data.get('language', 'English')
    
    global_app_instance.is_generating = True

    try:
        result = global_app_instance.processor.process(text, action="Grammar", context=context, language=language)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        global_app_instance.is_generating = False


@app.route(ALTERNATIVE_API, methods=["POST"])
def alternative():

    data = request.json
    text = data.get('text', '')
    context = data.get('context', '')
    language = data.get('language', 'English')

    global_app_instance.is_generating = True

    try:
        result = global_app_instance.processor.process(text, action="Alternative", context=context, language=language)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        global_app_instance.is_generating = False

@app.route(TRANSLATING_API, methods=["POST"])
def translate():
    
    if not global_app_instance: return jsonify({"error": "App not ready"}), 500
        
    data = request.json
    text = data.get('text', '')
    context = data.get('context', '')
    language = data.get('language', 'English')
    
    global_app_instance.is_generating = True

    try:
        result = global_app_instance.processor.process(text, action="Translate", context=context, language=language)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        global_app_instance.is_generating = False


@app.route(GENERATE_NEW_LINE_API, methods=["POST"])
def generate_new_line():

    data = request.json
    text = data.get('text', '')
    context = data.get('context', '')
    mode = data.get('mode', 'Copywriting')
    language = data.get('language', 'English')

    try:
        result = global_app_instance.processor.process(text, action="GenerateText", context=context, mode=mode, language=language)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        global_app_instance.is_generating = False


class Api:
    def set_mode(self, mode):
        if global_app_instance: global_app_instance.current_mode = mode
        
    def set_language(self, lang):
        if global_app_instance: global_app_instance.current_language = lang
        
    def clear_context(self):
        if global_app_instance: global_app_instance.context_text = ""
        
    def hide_window(self):
        if global_app_instance and global_app_instance.window:
            global_app_instance.window.hide()
            
    def copy_text(self, text):
        pyperclip.copy(text)
            
    def replace_text(self, text):
        if not global_app_instance: return
        
        replacement = text
        pyperclip.copy(replacement)
        
        if global_app_instance.window:
            global_app_instance.window.hide()
            
        time.sleep(0.1)
        keyboard.press_and_release('ctrl+v')
        
    def replace_text_next_line(self, text):
        if not global_app_instance: return
        
        replacement = global_app_instance.current_text + "\n" + text
        pyperclip.copy(replacement)
        
        if global_app_instance.window:
            global_app_instance.window.hide()
            
        time.sleep(0.1)
        keyboard.press_and_release('ctrl+v')

    def get_current_state(self):
        if not global_app_instance: return {}
        return {
            "text": global_app_instance.current_text,
            "context": global_app_instance.context_text,
            "mode": global_app_instance.current_mode,
            "language": global_app_instance.current_language
        }

class TypingAgentApp:
    def __init__(self):
        global global_app_instance
        global_app_instance = self
        
        self.processor = Processor()
        self.request_queue = queue.Queue()
        self.current_mode = "Standard"
        self.current_language = "English"
        self.current_text = ""
        self.context_text = ""
        self.is_generating = False
        
        self.api = Api()
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'index.html')
        
        self.window = webview.create_window(
            'Assistant',
            html_path,
            js_api=self.api,
            frameless=True,
            on_top=True,
            width=450,
            height=600,
            background_color='#0A0A0C',
            hidden=True
        )
        
    def on_context_hotkey(self):
        time.sleep(0.3)
        keyboard.release('ctrl')
        keyboard.release('alt')
        keyboard.release('c')
        keyboard.release('shift')
        text = get_selected_text()
        if text and text.strip():
            self.request_queue.put({"type": "context", "text": text})

    def on_hotkey(self):
        time.sleep(0.3)
        keyboard.release('ctrl')
        keyboard.release('alt')
        keyboard.release('w')
        keyboard.release('shift')
        text = get_selected_text()
        if text and text.strip():
            self.request_queue.put({"type": "show", "text": text})

    def process_queue(self):
        keyboard.add_hotkey('ctrl+alt+c', self.on_context_hotkey)
        keyboard.add_hotkey('ctrl+alt+w', self.on_hotkey)
        
        while True:
            try:
                item = self.request_queue.get(timeout=0.5)
                if item["type"] == "context":
                    self.context_text = item["text"]
                    escaped_text = json.dumps(self.context_text)
                    self.window.evaluate_js(f"updateContext({escaped_text})")
                    self.position_and_show()
                elif item["type"] == "show":
                    self.current_text = item["text"]
                    escaped_text = json.dumps(self.current_text)
                    self.window.evaluate_js(f"updateContext({escaped_text})")
                    self.position_and_show()
                    self.window.evaluate_js("resetUI()")
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Queue processing error: {e}")
                
    def position_and_show(self):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            width = 450
            height = 600
            
            # Center the window completely on the screen
            x = int((screen_width - width) / 2)
            y = int((screen_height - height) / 2)
            
            if x < 0 or y < 0: x, y = 50, 50 
            self.window.move(x, y)
        except Exception:
            pass
        self.window.show()

    def run(self):
        print("Select your text and press CTRL + ALT + W")
        t = threading.Thread(target=self.process_queue, daemon=True)
        t.start()
        
        flask_thread = threading.Thread(target=lambda: app.run(host='127.0.0.1', port=3000, debug=False, use_reloader=False), daemon=True)
        flask_thread.start()
        
        webview.start(debug=False)

if __name__ == "__main__":
    agent_app = TypingAgentApp()
    agent_app.run()