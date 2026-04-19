import zipfile
import os
from dataclasses import dataclass
from typing import List

@dataclass
class Finding:
    type: str
    path: str
    severity: str

class DeepArchiveAnalyzer:
    def __init__(self, path: str):
        self.path = path
        self.findings: List[Finding] = []

    def scan(self):
        with zipfile.ZipFile(self.path, 'r') as z:
            for file in z.namelist():
                self._analyze_file(file)

    def _analyze_file(self, file: str):
        if ".git/" in file:
            self.findings.append(Finding(type="git_exposure", path=file, severity="HIGH"))
        if file.endswith(".apk"):
            self.findings.append(Finding(type="android_apk", path=file, severity="MEDIUM"))
        if "token" in file.lower() or "key" in file.lower():
            self.findings.append(Finding(type="possible_secret", path=file, severity="CRITICAL"))
        if file.endswith(".zip"):
            self.findings.append(Finding(type="nested_archive", path=file, severity="MEDIUM"))

    def report(self):
        for f in self.findings:
            print(f"[{f.severity}] {f.type} -> {f.path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python archive_scanner.py <arquivo.zip>")
        sys.exit(1)
    analyzer = DeepArchiveAnalyzer(sys.argv[1])
    analyzer.scan()
    analyzer.report()
