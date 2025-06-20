import sys
import random
import math
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QSizePolicy, QMenu, QColorDialog)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QVariantAnimation, QRect, QSequentialAnimationGroup, QParallelAnimationGroup, QPointF, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QPainter, QBrush, QPen, QRadialGradient, QConicalGradient
from PIL import ImageGrab
from script import generate_poem, generate_7poem, name_list, random_name, common_chars, use_deepseek_poem
import requests
import json
import colorsys

class MinimizedWidget(QWidget):
    """Small draggable circle for minimized state"""
    clicked = pyqtSignal()  # Signal emitted when clicked (not dragged)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Use stay-on-top with Tool window type to prevent focus stealing
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(30, 30)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setAttribute(Qt.WA_ShowWithoutActivating)  # Don't steal focus when shown
        #self.setAttribute(Qt.WA_X11DoNotAcceptFocus)  # Don't accept focus on X11 systems
        
        # Dragging variables
        self.dragging = False
        self.drag_position = None
        self.drag_started = False
        
        # Minimal timer to ensure it stays visible without focus stealing
        self.stay_visible_timer = QTimer(self)
        self.stay_visible_timer.timeout.connect(self.ensure_visible)
        self.stay_visible_timer.start(-1)  # Check every 10 seconds, less frequently
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw white circle with light gray border (bright theme)
        painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.drawEllipse(2, 2, 26, 26)
        
        # Draw a small blue dot in center to indicate it's interactive
        painter.setBrush(QBrush(QColor(70, 130, 180)))  # Steel blue
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(12, 12, 6, 6)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_started = False
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            if not self.drag_started:
                # Mark that dragging has started
                self.drag_started = True
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.dragging and not self.drag_started:
                # This was a click, not a drag
                self.clicked.emit()
            self.dragging = False
            self.drag_started = False
            event.accept()
        elif event.button() == Qt.RightButton:
            # Right click to quit application
            QApplication.quit()
            
    def ensure_visible(self):
        """Ensure the widget stays visible without ever stealing focus"""
        if self.isVisible():
            # Simply raise the widget without any focus manipulation
            # The Qt.Tool flag should prevent focus stealing
            self.raise_()
            
            # Only re-apply window flags if they've been lost (rare case)
            current_flags = self.windowFlags()
            if not (current_flags & Qt.WindowStaysOnTopHint):
                # Store current focus before making changes
                current_focus = QApplication.focusWidget()
                
                # Re-apply flags and show
                self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
                self.setAttribute(Qt.WA_ShowWithoutActivating)
                self.setAttribute(Qt.WA_X11DoNotAcceptFocus)
                self.show()
                
                # Restore focus immediately if it was stolen
                #current_focus.setFocus()

class ModernButton(QPushButton):
    _style_sheet = '''
        QPushButton {
            color: white;
            border: none;
            font-size: 16px;
            /* Size is handled in init */
        }
        QPushButton:hover {
            /* Hover effect is handled in paintEvent */
        }
    '''
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        # Fixed properties
        self.setFixedSize(100, 30)  # Compact button size
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(self._style_sheet)
        
        # Animation properties
        self._pulse_factor = 0.0
        self._animation = QVariantAnimation()
        self._animation.setDuration(350)  # Longer for a visible, smoother pulse
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.OutQuad)
        self._animation.valueChanged.connect(self._update_pulse_factor)
        
        # Click handling
        self._is_animating = False
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.setInterval(200)  # Debounce interval for rapid clicks
        
    def _update_pulse_factor(self, value):
        if isinstance(value, (int, float)):
            self._pulse_factor = value
            self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # Define dark theme colors
        base_color_start = QColor(70, 130, 180)     # Steel blue
        base_color_end = QColor(100, 149, 237)      # Cornflower blue
        
        hover_color_start = QColor(100, 149, 237)   # Cornflower blue
        hover_color_end = QColor(135, 206, 250)     # Light sky blue

        pulse_color_start = QColor(135, 206, 250)   # Light sky blue
        pulse_color_end = QColor(173, 216, 230)     # Light blue

        # Choose color based on mouse state
        current_start_color = hover_color_start if self.underMouse() else base_color_start
        current_end_color = hover_color_end if self.underMouse() else base_color_end

        # Apply pulse animation effect
        if self._pulse_factor > 0:
            r_start = int(current_start_color.red() * (1 - self._pulse_factor) + pulse_color_start.red() * self._pulse_factor)
            g_start = int(current_start_color.green() * (1 - self._pulse_factor) + pulse_color_start.green() * self._pulse_factor)
            b_start = int(current_start_color.blue() * (1 - self._pulse_factor) + pulse_color_start.blue() * self._pulse_factor)
            final_start_color = QColor(r_start, g_start, b_start)

            r_end = int(current_end_color.red() * (1 - self._pulse_factor) + pulse_color_end.red() * self._pulse_factor)
            g_end = int(current_end_color.green() * (1 - self._pulse_factor) + pulse_color_end.green() * self._pulse_factor)
            b_end = int(current_end_color.blue() * (1 - self._pulse_factor) + pulse_color_end.blue() * self._pulse_factor)
            final_end_color = QColor(r_end, g_end, b_end)
        else:
            final_start_color = current_start_color
            final_end_color = current_end_color

        # Create simple solid color for dark theme
        painter.setBrush(QBrush(final_start_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, w, h, 12, 12)
        
        # Draw text with better contrast for dark theme
        painter.setPen(Qt.white)
        painter.setFont(self.font())
        painter.drawText(QRect(0, 0, w, h), Qt.AlignCenter, self.text())
        
    def mousePressEvent(self, event):
        # Handle rapid clicking with debounce
        if not self._is_animating and not self._click_timer.isActive():
            self._animate_click()
            self._click_timer.start()
        super().mousePressEvent(event)
        
    def _animate_click(self):
        # Stop any running animations
        if self._animation.state() == QPropertyAnimation.Running:
            self._animation.stop()
            
        # Start new animation
        self._is_animating = True
        self._animation.setDirection(QPropertyAnimation.Forward)
        
        # Disconnect any existing connections to avoid multiple connections
        try:
            self._animation.finished.disconnect()
        except TypeError:
            pass
            
        self._animation.finished.connect(self._reverse_animation)
        self._animation.start()
        
    def _reverse_animation(self):
        # Clean disconnect previous connection
        try:
            self._animation.finished.disconnect()
        except TypeError:
            pass
            
        # Reverse the animation
        self._animation.setDirection(QPropertyAnimation.Backward)
        self._animation.finished.connect(self._animation_finished)
        self._animation.start()
        
    def _animation_finished(self):
        # Clean disconnect and reset state
        try:
            self._animation.finished.disconnect()
        except TypeError:
            print("change")
            pass
            
        self._is_animating = False
    
    def enterEvent(self, event):
        self.update()  # Trigger repaint for hover effect
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.update()  # Trigger repaint to remove hover effect
        super().leaveEvent(event)

class AnimatedTextLabel(QLabel):
    """A label that animates each character with a color gradient while appearing"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.char_animations = {}  # Stores animations for each character
        self.char_opacities = {}   # Stores opacity values for each character
        self.full_text = ""       # The full text being displayed
        self.visible_chars = 0     # Number of currently visible characters
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setTextFormat(Qt.RichText)  # Enable rich text rendering

    def set_text_with_animation(self, text):
        """Set text with character-by-character animation"""
        # Store the full text
        self.full_text = text
        self.visible_chars = 0
        
        # Reset current animations
        for anim in self.char_animations.values():
            anim.stop()
        self.char_animations = {}
        self.char_opacities = {}
        
        # Start with an empty string
        self.setText("")
        
        # Add characters one by one with a delay
        for i, char in enumerate(text):
            # Create timer for this character
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda idx=i, c=char: self._add_character(idx, c))
            timer.start(30 * i)  # 30ms between each character
            
    def _add_character(self, index, char):
        """Add a character and start its color animation"""
        # Make sure we're not exceeding the length of full_text
        if index >= len(self.full_text):
            return
            
        # Increment the visible character count
        self.visible_chars += 1
        
        # Apply colored gradient to just the new character using HTML
        self.char_opacities[index] = 1.0  # Start with full color
        
        # Apply the text with color gradient for the new character
        self._update_text_with_colors()
        
        # Create animation to fade out the color
        anim = QVariantAnimation(self)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setDuration(800)  # Longer duration for smoother fade
        anim.valueChanged.connect(lambda val, idx=index: self._update_char_color(idx, val))
        anim.start()
        
        # Store the animation
        self.char_animations[index] = anim
    
    def _update_char_color(self, index, value):
        """Update the color intensity for a specific character"""
        self.char_opacities[index] = value
        self._update_text_with_colors()
    
    def _update_text_with_colors(self):
        html_text = ""
        for i, char in enumerate(self.full_text):
            if i >= self.visible_chars:
                continue
            if char == '<':
                safe_char = '&lt;'
            elif char == '>':
                safe_char = '&gt;'
            elif char == '&':
                safe_char = '&amp;'
            elif char == '\n':
                safe_char = '<br>'
            else:
                safe_char = char
            if i in self.char_opacities and self.char_opacities[i] > 0:
                opacity = self.char_opacities[i]
                # Blend from blue gradient (100, 150, 255) to normal text color (51, 51, 51)
                r = int(100 * opacity + 51 * (1 - opacity))
                g = int(150 * opacity + 51 * (1 - opacity))
                b = int(255 * opacity + 51 * (1 - opacity))
                html_text += f"<span style='color: rgb({r},{g},{b});'>{safe_char}</span>"
            else:
                html_text += safe_char
        self.setText(html_text)

class ModernCard(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #3a3a3a;
                border-radius: 16px;
                padding: 12px;
                font-size: 22px;
                color: #ffffff;
                font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
                line-height: 1.8;
                margin: 2px;
                border: 1px solid #555555;
            }
        """)
        self.setWordWrap(True)
        
        # Create animated text label as child widget
        self.animated_label = AnimatedTextLabel(self)
        self.animated_label.setStyleSheet("""
            background-color: transparent;
            font-size: 22px;
            font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            line-height: 1.8;
            padding: 0px;
            margin: 0px;
        """)
        self.animated_label.setTextFormat(Qt.RichText)
        
        # Layout to hold the animated label
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(self.animated_label)
        self.setLayout(layout)
        
        # Animation fade properties
        self._fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self._fade_out_animation.setDuration(200)  # Faster fade out
        self._fade_out_animation.setStartValue(1.0)
        self._fade_out_animation.setEndValue(0.0)
        
        self._fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self._fade_in_animation.setDuration(200)  # Faster fade in
        self._fade_in_animation.setStartValue(0.0)
        self._fade_in_animation.setEndValue(1.0)
        
    def set_animated_text(self, text):
        """Set text with character-by-character animation"""
        # Start with fade out if there's existing visible text
        if self.text():
            # Connect fade out animation to start the new text animation when done
            try:
                self._fade_out_animation.finished.disconnect()
            except TypeError:
                pass
                
            self._fade_out_animation.finished.connect(lambda: self._start_animation(text))
            self._fade_out_animation.start()
        else:
            # If no existing text, just start the character animation
            self._start_animation(text)
    
    def _start_animation(self, text):
        # Disconnect signal if connected
        try:
            self._fade_out_animation.finished.disconnect()
        except TypeError:
            pass
            
        # Clear old text
        self.setText("")  
        self.setWindowOpacity(1.0)
        
        # Start character animation in the child widget
        self.animated_label.set_text_with_animation(text)
    

    


class ModernApp(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize all instance variables first
        self.auto_mode = False
        self.auto_screenshot = False
        self.idle_timer = None
        self.auto_poem_timer = None
        self.screenshot_timer = None
        self.poem_card = None
        
        # Create screenshots directory if it doesn't exist
        os.makedirs('C:/Screenshots', exist_ok=True)
        self.name_card = None
        self.btn_poem = None
        self.btn_name = None
        self.poem_cooldown = False  # Track poem button cooldown state
        
        # Minimized state
        self.is_minimized = False
        self.minimized_widget = None
        self.normal_position = None
        
        # Setup window - borderless with bright theme
        self.setWindowTitle("随机五言绝句生成器")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(220, 320)  # Compact size with minimal borders
        
        # Restore original stylesheet for background
        self.setStyleSheet('''
            QWidget {
                font-size: 10px;
                margin: 0px;
                padding: 0px;
            }
        ''')
        
        # Initialize UI and timers
        self.init_ui()
        self.init_timers()
        
        # Center window on screen
        self.center()
        
        # Variables for window dragging
        self.dragging = False
        self.drag_position = None
        
    def center(self):
        frame_geometry = self.frameGeometry()
        center_point = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        
    def init_ui(self):
        # Main layout with minimal spacing
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Title bar with close button
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        title_bar_layout.setSpacing(0)
        
        # Title (draggable area)
        self.title_label = TitleLabel("随机五言绝句生成器")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                margin: 2px 0;
                padding: 0px;
                font-family: 'Microsoft YaHei', sans-serif;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        title_bar_layout.addWidget(self.title_label, 1)
        
        # Custom close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #e57373;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ef9a9a;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.close_button.clicked.connect(self.minimize_to_circle)
        title_bar_layout.addWidget(self.close_button)
        
        main_layout.addLayout(title_bar_layout)
        
        # Poem card with bright theme
        self.poem_card = ModernCard()
        self.poem_card.setMinimumHeight(170)
        self.poem_card.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 16px;
                padding: 0.5px;
                font-size: 22px;
                color: #222222;
                font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
                line-height: 1.8;
                margin: 2px;
            }
        """)
        main_layout.addWidget(self.poem_card, 1)
        
        # Name card with bright theme
        self.name_card = ModernCard()
        self.name_card.setMinimumHeight(40)
        self.name_card.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 16px;
                padding: 8px;
                font-size: 16px;
                font-weight: bold;
                color: #222222;
                font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
                margin: 2px;
            }
        """)
        main_layout.addWidget(self.name_card, 0)
        
        # Buttons layout with fixed sizes
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(12)
        
        # Generate poem button
        self.btn_poem = ModernButton("生成诗句")
        self.btn_poem.clicked.connect(self.show_poem)
        buttons_layout.addWidget(self.btn_poem, alignment=Qt.AlignCenter)
        
        # Generate name button
        self.btn_name = ModernButton("随机姓名")
        self.btn_name.clicked.connect(self.show_name)
        buttons_layout.addWidget(self.btn_name, alignment=Qt.AlignCenter)
        
        main_layout.addLayout(buttons_layout)
        
        # Set main layout
        self.setLayout(main_layout)
        
        # Initial poem
        self.show_poem()
        
    def init_timers(self):
        # Clean up existing timers if any
        if hasattr(self, 'idle_timer') and self.idle_timer:
            try:
                self.idle_timer.stop()
                self.idle_timer.deleteLater()
            except:
                pass
                
        if hasattr(self, 'auto_poem_timer') and self.auto_poem_timer:
            try:
                self.auto_poem_timer.stop()
                self.auto_poem_timer.deleteLater()
            except:
                pass
        
        # Set up idle timer to 4 minutes
        self.idle_timer = QTimer(self)
        self.idle_timer.setTimerType(Qt.VeryCoarseTimer)
        self.idle_timer.setInterval(240000)  # 4 minutes (240,000 ms)
        self.idle_timer.timeout.connect(self.start_auto_poem)
        self.idle_timer.start()
        
        # Auto poem timer (20 seconds per poem)
        self.auto_poem_timer = QTimer(self)
        self.auto_poem_timer.setTimerType(Qt.VeryCoarseTimer)
        self.auto_poem_timer.setInterval(20000)  # 20 seconds per poem in auto mode
        self.auto_poem_timer.timeout.connect(self.auto_generate_poem)
        
        # Screenshot timer - synchronized with auto poem timer
        self.screenshot_timer = QTimer(self)
        self.screenshot_timer.setTimerType(Qt.VeryCoarseTimer)
        self.screenshot_timer.setInterval(20000)  # 20 seconds per screenshot, matching poem generation
        self.screenshot_timer.timeout.connect(self.take_screenshot)
        
    # Mouse events for window dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_label.geometry().contains(event.pos()):
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        self.dragging = False
        
    def minimize_to_circle(self):
        """Minimize the main window to a small draggable circle"""
        if self.is_minimized:
            return
        # Save current position
        self.normal_position = self.pos()
        # Create minimized widget if it doesn't exist
        if not self.minimized_widget:
            self.minimized_widget = MinimizedWidget()
            self.minimized_widget.clicked.connect(self.restore_from_circle)
        # Position the circle where the close button was
        close_button_global = self.close_button.mapToGlobal(self.close_button.rect().center())
        circle_pos_x = close_button_global.x() - 15
        circle_pos_y = close_button_global.y() - 15
        self.minimized_widget.move(circle_pos_x, circle_pos_y)
        # Save the circle's position for restoration
        self.circle_last_pos = self.minimized_widget.pos()
        # Show circle and hide main window without stealing focus
        current_focus = QApplication.focusWidget()
        self.minimized_widget.show()
        self.minimized_widget.raise_()
        self.hide()
        self.is_minimized = True

    def restore_from_circle(self):
        """Restore the main window from the minimized circle, aligning the close button to the circle's position"""
        if not self.is_minimized:
            return
        # Hide the circle
        if self.minimized_widget:
            # Save the current position of the circle
            self.circle_last_pos = self.minimized_widget.pos()
            self.minimized_widget.hide()
        # Restore main window so that the close button aligns with the circle's position
        if hasattr(self, 'circle_last_pos') and self.circle_last_pos is not None:
            # Calculate offset: move window so that close button center aligns with circle
            close_btn_center = self.close_button.rect().center()
            # Get the offset of the close button center relative to the window
            close_btn_offset = self.close_button.mapTo(self, close_btn_center)
            # Move window so that close button center is at the circle's position
            new_x = self.circle_last_pos.x() - close_btn_offset.x()
            new_y = self.circle_last_pos.y() - close_btn_offset.y()
            self.move(new_x, new_y)
        elif self.normal_position:
            self.move(self.normal_position)
        self.show()
        self.raise_()
        self.activateWindow()
        self.is_minimized = False
        
    def reset_idle_timer(self):
        # Reset idle timer on user interaction
        # Stop auto mode if active
        if self.auto_mode:
            self.auto_mode = False
            self.auto_poem_timer.stop()
            if self.auto_screenshot:
                self.auto_screenshot = False
                self.screenshot_timer.stop()
            self.set_buttons_style(normal=True)
        
        # Reset idle timer
        if hasattr(self, 'idle_timer') and self.idle_timer:
            self.idle_timer.stop()
            self.idle_timer.start()
        else:
            # If there's any issue with the timer, reinitialize it
            self.init_timers()
        
    def set_buttons_style(self, normal=False):
        # In auto mode, we don't apply custom styles as the ModernButton 
        # now handles appearance through its paintEvent
        if normal:
            # Just trigger a repaint to restore normal state
            self.btn_poem.update()
            self.btn_name.update()
        else:
            # For auto mode, we'll just animate the buttons
            self.btn_poem._animate_click()
            self.btn_name._animate_click()
    
    def start_auto_poem(self):
        self.auto_mode = True
        self.auto_screenshot = True
        self.auto_poem_timer.start()
        self.screenshot_timer.start()
        self.set_buttons_style(normal=False)
        self.auto_generate_poem()
        # Take initial screenshot
        self.take_screenshot()
        
    def auto_generate_poem(self):
        if self.auto_mode:
            new_poem = generate_poem()
            self.poem_card.set_animated_text(new_poem)
    
    def show_poem(self):
        # Check if button is on cooldown
        if self.poem_cooldown:
            return
            
        # Set cooldown
        self.poem_cooldown = True
        self.btn_poem.setDisabled(True)
        
        # Reset idle timer
        self.reset_idle_timer()
        
        # Use DeepSeek if last selected name was 周歆然 and not in auto mode
        if globals().get('use_deepseek_poem', False) == True and not self.auto_mode:
            new_poem = deepseek_generate_poem()
        else:
            new_poem = generate_poem()
        self.poem_card.set_animated_text(new_poem)
        
        # Calculate animation duration based on poem length + base time
        cooldown_duration = len(new_poem) * 30 + 400  # 30ms per character + 400ms base
        QTimer.singleShot(cooldown_duration, self.enable_poem_button)
    
    def show_name(self):
        self.reset_idle_timer()
        name = random_name()
        self.name_card.setText(name)
        self.animate_card(self.name_card)
        
        # Add cooldown for 汤子昂 button
        if "汤子昂" in name:
            self.btn_name.setDisabled(True)
            QTimer.singleShot(1200, self.enable_name_button)
    
    def enable_name_button(self):
        self.btn_name.setDisabled(False)
    
    def animate_card(self, widget):
        # Fade in animation - used for name card only now
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        
    def enable_poem_button(self):
        # Re-enable poem button after cooldown
        self.poem_cooldown = False
        self.btn_poem.setDisabled(False)
    
    def take_screenshot(self):
        if not self.auto_screenshot:
            return
            
        # Get current timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:/Screenshots/poem_screenshot_{timestamp}.png"
        
        # Take screenshot of the window
        try:
            # Use PyQt's geometry to get window position
            x, y = self.geometry().x(), self.geometry().y()
            width, height = self.geometry().width(), self.geometry().height()
            
            # Capture the screenshot using PIL
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            screenshot.save(filename)
            
            # Check if we have exceeded the limit of 300 screenshots
            self.manage_screenshot_limit(300)
        except Exception as e:
            print(f"Screenshot error: {e}")
            
    def manage_screenshot_limit(self, max_screenshots=300):
        """Ensure the screenshots folder doesn't exceed the maximum number of images"""
        try:
            screenshot_dir = "C:/Screenshots"
            # Get list of all screenshot files
            screenshots = [os.path.join(screenshot_dir, f) for f in os.listdir(screenshot_dir) 
                          if f.lower().endswith('.png') and f.startswith('poem_screenshot_')]
            
            # If we have more screenshots than the limit
            if len(screenshots) > max_screenshots:
                # Sort by creation/modification time (oldest first)
                screenshots.sort(key=os.path.getctime)
                
                # Calculate how many to remove
                to_delete = len(screenshots) - max_screenshots
                
                # Remove oldest screenshots
                for i in range(to_delete):
                    try:
                        os.remove(screenshots[i])
                    except Exception as e:
                        print(f"Error deleting old screenshot {screenshots[i]}: {e}")
        except Exception as e:
            print(f"Error managing screenshot limit: {e}")
    
    def closeEvent(self, event):
        # Safely stop all timers if they exist
        if hasattr(self, 'idle_timer') and self.idle_timer:
            self.idle_timer.stop()
        if hasattr(self, 'auto_poem_timer') and self.auto_poem_timer:
            self.auto_poem_timer.stop()
        if hasattr(self, 'screenshot_timer') and self.screenshot_timer:
            self.screenshot_timer.stop()
        
        # Clean up minimized widget
        if hasattr(self, 'minimized_widget') and self.minimized_widget:
            self.minimized_widget.close()
            
        event.accept()
        QApplication.quit()

class TitleLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_settings_menu)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.show_settings_menu(event.pos())
        else:
            super().mousePressEvent(event)

    def show_settings_menu(self, pos):
        menu = QMenu(self)
        color_action = menu.addAction('Change Theme Color...')
        action = menu.exec_(self.mapToGlobal(pos))
        if action == color_action:
            color = QColorDialog.getColor(self.palette().color(QPalette.WindowText), self, 'Select Theme Color')
            if color.isValid():
                self.theme_color_changed.emit(color)

def deepseek_generate_poem():
    """
    Calls DeepSeek API to generate a 4-line, 5-character-per-line Chinese poem and returns it as a string.
    The format must match the local generator: 4 lines, each 5 Chinese characters, separated by newlines.
    """
    API_KEY = 'sk-d56933595d834a22af8349a6a300cf5c'  # Replace with your actual DeepSeek API key
    url = 'https://api.deepseek.com/chat/completions'  # Updated API endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    prompt = (
        "请生成一首4句、每句5个汉字的中国古风诗，每句换行，输出格式严格为4行，每行5个汉字，不要标点，不要多余解释。"
        "确保每行都是完整的5个汉字，不要包含任何数字、标点符号或额外文字。"
    )
    data = {
        "model": "deepseek-chat",  # Updated model name
        "messages": [
            {"role": "system", "content": "你是一个中国古诗专家，擅长创作五言绝句。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,  # Slightly lower temperature for more focused output
        "max_tokens": 100
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        result = response.json()
        poem = result['choices'][0]['message']['content'].strip()
        
        # Clean up the response to ensure proper format
        lines = []
        for line in poem.splitlines():
            line = line.strip()
            # Remove any non-Chinese characters and take first 5 characters
            chinese_only = ''.join([c for c in line if '\u4e00' <= c <= '\u9fff'])
            if chinese_only and len(chinese_only) >= 5:
                lines.append(chinese_only[:5])
                if len(lines) >= 4:  # Stop after we have 4 lines
                    break
                    
        if len(lines) >= 4:
            return '\n'.join(lines[:4])
        return "生成失败，请重试"  # Fallback message if we couldn't get valid output
    except Exception as e:
        return "（DeepSeek诗歌生成失败）"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set font
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window = ModernApp()
    window.show()
    sys.exit(app.exec_())
