import sys
import time
import random
from seleniumbase import SB
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QSpinBox, 
                            QPushButton, QFormLayout, QGroupBox, QMessageBox,
                            QScrollArea, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap


class EbayBotThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, proxy, keyword, product_index, num_runs):
        super().__init__()
        self.proxy = proxy
        self.keyword = keyword
        self.product_index = product_index
        self.num_runs = num_runs
        self.running = True
        
    def run(self):
        run_count = 0
        
        while run_count < self.num_runs and self.running:
            run_count += 1
            self.update_signal.emit(f"Starting run {run_count} of {self.num_runs}...")
            
            try:
                #
                with SB(uc=True, proxy=self.proxy) as sb:
                    try:
                        self.update_signal.emit("Opening eBay...")
                        sb.open("https://www.ebay.com/")
                        sb.sleep(3)
                        
                        try:
                            sb.maximize_window()
                            time.sleep(3)
                            
                            search_box = 'input.gh-search-input[placeholder="Search for anything"]'
                            self.update_signal.emit("Clicking search box...")
                            sb.click(search_box, timeout=10)
                            sb.sleep(2)
                            
                            # Type the keyword with random delay
                            self.update_signal.emit(f"Typing search keyword: {self.keyword}")
                            for char in self.keyword:
                                sb.send_keys(search_box, char, by="css selector", timeout=10)
                                time.sleep(random.uniform(0.1, 0.3))

                            sb.send_keys(search_box, "\n")  # Press Enter
                            self.update_signal.emit("Waiting for search results...")
                            sb.sleep(4)  # Wait for results to load

                            # Target the specified item in the search results
                            try:
                                self.update_signal.emit(f"Selecting product at index {self.product_index}...")
                                item_selector = ".srp-results.srp-grid.clearfix li.s-item.s-item__pl-on-bottom"
                                product_selector = sb.find_elements(item_selector)
                                
                                if len(product_selector) >= self.product_index:
                                    product_selector[self.product_index-1].click()
                                    
                                    try:
                                        self.update_signal.emit("Viewing product details...")
                                        sb.sleep(3)  # Allow item page to load
                                        sb.switch_to_window(1)
                                        
                                        # Scroll the product detail page slowly
                                        self.update_signal.emit("Scrolling through product page...")
                                        for i in range(0, 2000, 200):
                                            sb.execute_script(f"window.scrollTo(0, {i});")
                                            time.sleep(0.5)
                                    except Exception as e:
                                        self.update_signal.emit(f"Error while viewing details: {str(e)}. Moving to next run.")
                                else:
                                    self.update_signal.emit(f"Error: Could not find product at index {self.product_index}. Moving to next run.")
                            except Exception as e:
                                self.update_signal.emit(f"Error selecting product: {str(e)}. Moving to next run.")
                        except Exception as e:
                            self.update_signal.emit(f"Error with search: {str(e)}. Moving to next run.")
                    except Exception as e:
                        self.update_signal.emit(f"Error opening eBay: {str(e)}. Moving to next run.")
            except Exception as e:
                self.update_signal.emit(f"Error initializing browser: {str(e)}. Moving to next run.")
            
            self.update_signal.emit(f"Completed run {run_count} of {self.num_runs}")
        
        self.update_signal.emit("All runs completed!")
        self.finished_signal.emit()
    
    def stop(self):
        self.running = False


class EbayBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("eBay Bot")
        self.setFixedSize(600, 550)
        self.bot_thread = None
        
        # Set up the UI
        self.init_ui()
        
    def init_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel("eBay Bot")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0063D1; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Proxy settings group
        proxy_group = QGroupBox("Proxy Settings")
        proxy_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        proxy_layout = QFormLayout()
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("username:password@host:port")
        proxy_layout.addRow("Proxy:", self.proxy_input)
        
        proxy_help = QLabel("Example: user123:pass456@proxy.example.com:8080")
        proxy_help.setStyleSheet("color: gray; font-size: 10px;")
        proxy_layout.addRow("", proxy_help)
        
        proxy_group.setLayout(proxy_layout)
        main_layout.addWidget(proxy_group)
        
        # Search settings group
        search_group = QGroupBox("Search Settings")
        search_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        search_layout = QFormLayout()
        
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter search keyword")
        search_layout.addRow("Keyword:", self.keyword_input)
        
        self.product_index = QSpinBox()
        self.product_index.setMinimum(1)
        self.product_index.setMaximum(48)
        self.product_index.setValue(1)
        search_layout.addRow("Product Index:", self.product_index)
        
        self.num_runs = QSpinBox()
        self.num_runs.setMinimum(1)
        self.num_runs.setMaximum(100)
        self.num_runs.setValue(1)
        search_layout.addRow("Number of Runs:", self.num_runs)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Bot")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #0063D1;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052AB;
            }
        """)
        self.start_button.clicked.connect(self.start_bot)
        
        self.stop_button = QPushButton("Stop Bot")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #E3242B;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C21E25;
            }
        """)
        self.stop_button.clicked.connect(self.stop_bot)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        main_layout.addLayout(button_layout)
        
        # Status
        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setText("Ready")
        self.status_text.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        self.status_text.setMinimumHeight(150)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.status_text)
        scroll_area.setWidgetResizable(True)
        status_layout.addWidget(scroll_area)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Set the main widget
        self.setCentralWidget(main_widget)
    
    def update_status(self, message):
        current_text = self.status_text.toPlainText()
        new_text = current_text + "\n" + message if current_text != "Ready" else message
        self.status_text.setText(new_text)
        # Auto-scroll to the bottom to show the latest status
        self.status_text.verticalScrollBar().setValue(self.status_text.verticalScrollBar().maximum())
    
    def start_bot(self):
        proxy = self.proxy_input.text()
        keyword = self.keyword_input.text()
        product_idx = self.product_index.value()
        runs = self.num_runs.value()
        
        if not proxy or not keyword:
            QMessageBox.warning(self, "Missing Information", 
                               "Please fill in all required fields (proxy and keyword).")
            return
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_text.setText("Starting bot...")
        
        # Start the bot in a separate thread
        self.bot_thread = EbayBotThread(proxy, keyword, product_idx, runs)
        self.bot_thread.update_signal.connect(self.update_status)
        self.bot_thread.finished_signal.connect(self.on_bot_finished)
        self.bot_thread.start()
    
    def stop_bot(self):
        if self.bot_thread and self.bot_thread.isRunning():
            self.update_status("Stopping bot...")
            self.bot_thread.stop()
    
    def on_bot_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.update_status("Bot stopped")
    
    def closeEvent(self, event):
        if self.bot_thread and self.bot_thread.isRunning():
            self.bot_thread.stop()
            self.bot_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = EbayBotApp()
    window.show()
    sys.exit(app.exec_())
