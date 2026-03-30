#! /usr/bin/env python
# Copyright 2026

import logging
import sys
from pathlib import Path

from facturx import generate_from_file
from facturx.facturx import logger

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFileDialog,
        QFormLayout,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover - runtime guard only
    print("PySide6 is required for this GUI. Install it with: pip install PySide6")
    sys.exit(1)


LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
}


class PdfGenQtWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Factur-X PDF Generator")
        self.resize(900, 700)
        self._build_ui()

    def _build_ui(self):
        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        files_group = QGroupBox("Files")
        files_layout = QGridLayout(files_group)
        layout.addWidget(files_group)

        self.pdf_input = QLineEdit()
        self.xml_input = QLineEdit()
        self.output_input = QLineEdit()

        pdf_button = QPushButton("Browse...")
        pdf_button.clicked.connect(self._choose_pdf)
        xml_button = QPushButton("Browse...")
        xml_button.clicked.connect(self._choose_xml)
        output_button = QPushButton("Browse...")
        output_button.clicked.connect(self._choose_output_pdf)

        files_layout.addWidget(QLabel("Input PDF"), 0, 0)
        files_layout.addWidget(self.pdf_input, 0, 1)
        files_layout.addWidget(pdf_button, 0, 2)
        files_layout.addWidget(QLabel("Input XML"), 1, 0)
        files_layout.addWidget(self.xml_input, 1, 1)
        files_layout.addWidget(xml_button, 1, 2)
        files_layout.addWidget(QLabel("Output PDF"), 2, 0)
        files_layout.addWidget(self.output_input, 2, 1)
        files_layout.addWidget(output_button, 2, 2)

        attachment_group = QGroupBox("Optional Attachments")
        attachment_layout = QVBoxLayout(attachment_group)
        layout.addWidget(attachment_group)

        self.attachment_list = QListWidget()
        attachment_layout.addWidget(self.attachment_list)
        attachment_buttons = QHBoxLayout()
        add_attachment_button = QPushButton("Add Attachment")
        add_attachment_button.clicked.connect(self._add_attachment)
        remove_attachment_button = QPushButton("Remove Selected")
        remove_attachment_button.clicked.connect(self._remove_selected_attachment)
        attachment_buttons.addWidget(add_attachment_button)
        attachment_buttons.addWidget(remove_attachment_button)
        attachment_layout.addLayout(attachment_buttons)

        options_group = QGroupBox("Options")
        options_layout = QFormLayout(options_group)
        layout.addWidget(options_group)

        self.log_level_input = QComboBox()
        self.log_level_input.addItems(["info", "debug", "warn", "error"])

        self.flavor_input = QComboBox()
        self.flavor_input.addItems(["autodetect", "factur-x", "order-x"])

        self.level_input = QComboBox()
        self.level_input.addItems(
            [
                "autodetect",
                "minimum",
                "basicwl",
                "basic",
                "en16931",
                "extended",
                "comfort",
            ]
        )

        self.orderx_type_input = QComboBox()
        self.orderx_type_input.addItems(
            ["autodetect", "order", "order_change", "order_response"]
        )

        self.afrelationship_input = QComboBox()
        self.afrelationship_input.addItems(["data", "source", "alternative"])

        self.lang_input = QLineEdit()

        self.meta_author_input = QLineEdit()
        self.meta_keywords_input = QLineEdit()
        self.meta_title_input = QLineEdit()
        self.meta_subject_input = QLineEdit()

        self.disable_xsd_check_input = QCheckBox("Disable XSD check")
        self.disable_schematron_check_input = QCheckBox("Disable Schematron check")
        self.disable_xmp_compression_input = QCheckBox("Disable XMP compression")
        self.overwrite_input = QCheckBox("Overwrite output file if it exists")

        options_layout.addRow("Log level", self.log_level_input)
        options_layout.addRow("Flavor", self.flavor_input)
        options_layout.addRow("Level", self.level_input)
        options_layout.addRow("Order-X type", self.orderx_type_input)
        options_layout.addRow("Language (RFC 3066)", self.lang_input)
        options_layout.addRow("AFRelationship", self.afrelationship_input)
        options_layout.addRow("Metadata author", self.meta_author_input)
        options_layout.addRow("Metadata keywords", self.meta_keywords_input)
        options_layout.addRow("Metadata title", self.meta_title_input)
        options_layout.addRow("Metadata subject", self.meta_subject_input)
        options_layout.addRow(self.disable_xsd_check_input)
        options_layout.addRow(self.disable_schematron_check_input)
        options_layout.addRow(self.disable_xmp_compression_input)
        options_layout.addRow(self.overwrite_input)

        controls = QHBoxLayout()
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        generate_button = QPushButton("Generate")
        generate_button.clicked.connect(self._generate)
        controls.addWidget(generate_button)
        controls.addWidget(self.status_label, stretch=1)
        layout.addLayout(controls)

    def _choose_pdf(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select input PDF", "", "PDF files (*.pdf);;All files (*)"
        )
        if filename:
            self.pdf_input.setText(filename)
            if not self.output_input.text().strip():
                source = Path(filename)
                self.output_input.setText(
                    str(source.with_name(f"{source.stem}-facturx{source.suffix}"))
                )

    def _choose_xml(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select input XML", "", "XML files (*.xml);;All files (*)"
        )
        if filename:
            self.xml_input.setText(filename)

    def _choose_output_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select output PDF", "", "PDF files (*.pdf);;All files (*)"
        )
        if filename:
            self.output_input.setText(filename)

    def _add_attachment(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self, "Select attachment(s)", "", "All files (*)"
        )
        for filename in filenames:
            self.attachment_list.addItem(filename)

    def _remove_selected_attachment(self):
        for item in self.attachment_list.selectedItems():
            row = self.attachment_list.row(item)
            self.attachment_list.takeItem(row)

    def _error(self, message: str):
        self.status_label.setText(message)
        QMessageBox.critical(self, "Error", message)

    def _generate(self):
        pdf_file = self.pdf_input.text().strip()
        xml_file = self.xml_input.text().strip()
        output_file = self.output_input.text().strip()

        for path, label in (
            (pdf_file, "Input PDF"),
            (xml_file, "Input XML"),
            (output_file, "Output PDF"),
        ):
            if not path:
                self._error(f"{label} is required.")
                return

        input_files = [pdf_file, xml_file] + [
            self.attachment_list.item(i).text() for i in range(self.attachment_list.count())
        ]
        for filepath in input_files:
            if not Path(filepath).is_file():
                self._error(f"File does not exist: {filepath}")
                return

        output_path = Path(output_file)
        if output_path.is_dir():
            self._error(f"Output PDF is a directory: {output_file}")
            return
        if output_path.exists() and not self.overwrite_input.isChecked():
            self._error(
                f"Output file already exists: {output_file}. "
                "Enable overwrite to replace it."
            )
            return

        logger.setLevel(LOG_LEVELS[self.log_level_input.currentText()])
        attachments = {}
        for i in range(self.attachment_list.count()):
            filepath = self.attachment_list.item(i).text()
            attachments[Path(filepath).name] = {"filepath": filepath}

        meta_values = {
            "author": self.meta_author_input.text().strip() or None,
            "keywords": self.meta_keywords_input.text().strip() or None,
            "title": self.meta_title_input.text().strip() or None,
            "subject": self.meta_subject_input.text().strip() or None,
        }
        pdf_metadata = None if all(value is None for value in meta_values.values()) else meta_values

        try:
            generate_from_file(
                pdf_file,
                xml_file,
                check_xsd=not self.disable_xsd_check_input.isChecked(),
                check_schematron=not self.disable_schematron_check_input.isChecked(),
                flavor=self.flavor_input.currentText(),
                level=self.level_input.currentText(),
                orderx_type=self.orderx_type_input.currentText(),
                pdf_metadata=pdf_metadata,
                lang=self.lang_input.text().strip() or None,
                output_pdf_file=output_file,
                attachments=attachments,
                afrelationship=self.afrelationship_input.currentText(),
                xmp_compression=not self.disable_xmp_compression_input.isChecked(),
            )
        except Exception as exc:
            self._error(f"Generation failed: {exc}")
            return

        message = f"Success. Generated PDF: {output_file}"
        self.status_label.setText(message)
        QMessageBox.information(self, "Success", message)


def main():
    app = QApplication(sys.argv)
    window = PdfGenQtWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
