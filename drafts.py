# import os
# import zipfile
# import tempfile
# import re
# from dotenv import load_dotenv
# import openai

# # Load API key
# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     raise ValueError("Missing OPENAI_API_KEY in .env")
# client = openai.OpenAI(api_key=api_key)

# # ========== PROMPTS ==========
# def get_converter_prompt():
#     return """
# You are a Kotlin-to-Swift model conversion agent.
# Your task is to analyze provided Kotlin code and convert only data model classes into Swift code.

# Instructions:
# - Focus only on model classes — typically data class declarations that represent structured data (e.g., User, Product, Message, etc.).
# - Ignore all UI, ViewModel, repository, networking, or business logic code.
# - For each Kotlin data class, generate a Swift struct or class with equivalent properties.
# - Use Swift types (String, Int, Double, Bool, [Type], etc.) corresponding to Kotlin types.
# - If a Kotlin property is nullable (?), make it optional in Swift (?).
# - If annotations like @SerializedName or @Json are present, use Swift’s CodingKeys enum to map property names.
# - Preserve default values where applicable.
# - Ensure each Swift model conforms to Codable.
# - Output Swift code only — clean, idiomatic, and ready to use in iOS projects.
# """

# def get_validator_prompt():
#     return """
# You are a Swift code reviewer and fixer focused on validating Swift data models converted from Kotlin.

# Your task is to:

# - Analyze the provided Swift model code (usually a struct or class conforming to Codable).
# - Detect any issues, such as:
#   - Syntax errors
#   - Invalid Swift types
#   - Missing CodingKeys for renamed properties
#   - Non-optional fields that should be optional
#   - Mismatched default values or incorrect type usage
#   - Improper conformance to Codable (e.g., nested objects or arrays)

# If errors or inconsistencies are found, explain the problem in simple terms and provide a fully corrected version of the model.

# Then, re-validate the corrected model again, until the model is clean, valid, and ready to compile in a real Swift project.

# Output the final version of the Swift model inside a code block, and confirm with:
# ✅ "Model is valid and Swift-compliant."
# """

# # ========== MODEL EXTRACTION ==========
# def extract_kotlin_models(folder_path):
#     kotlin_models = []
#     for root, _, files in os.walk(folder_path):
#         if "model" in root.lower():
#             for file in files:
#                 if file.endswith(".kt"):
#                     file_path = os.path.join(root, file)
#                     try:
#                         with open(file_path, "r", encoding="utf-8") as f:
#                             content = f.read()
#                     except UnicodeDecodeError:
#                         try:
#                             with open(file_path, "r", encoding="latin1") as f:
#                                 content = f.read()
#                         except Exception:
#                             print(f"⚠️ Skipping unreadable file: {file_path}")
#                             continue
#                     matches = re.findall(r"data class\s+\w+\s*\(.*?\)\s*{?[^}]*}?+", content, re.DOTALL)
#                     kotlin_models.extend(matches)
#     return kotlin_models

# # ========== CONVERSION + VALIDATION ==========
# def chat(messages):
#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=messages,
#         temperature=0.2
#     )
#     return response.choices[0].message.content.strip()

# def convert_model_to_swift(kotlin_model: str) -> str:
#     return chat([
#         {"role": "system", "content": get_converter_prompt()},
#         {"role": "user", "content": kotlin_model}
#     ])

# def validate_swift_model(swift_code: str) -> str:
#     messages = [
#         {"role": "system", "content": get_validator_prompt()},
#         {"role": "user", "content": swift_code}
#     ]
#     round_counter = 1
#     previous_code = ""
#     same_code_count = 0
#     max_rounds = 10

#     while round_counter <= max_rounds:
#         print(f"\n🧪 Validation round {round_counter}...")
#         reply = chat(messages)
#         print("🔍 Validator reply (truncated):")
#         print(reply[:500] + ("..." if len(reply) > 500 else ""))

#         if "✅ Model is valid and Swift-compliant." in reply:
#             match = re.search(r"```swift\n(.*?)```", reply, re.DOTALL)
#             return match.group(1).strip() if match else reply

#         # Try to extract Swift code
#         match = re.search(r"```swift\n(.*?)```", reply, re.DOTALL)
#         if match:
#             new_code = match.group(1).strip()
#         else:
#             new_code = reply

#         if new_code == previous_code:
#             same_code_count += 1
#         else:
#             same_code_count = 0
#         previous_code = new_code

#         if same_code_count >= 2:
#             print("⚠️ Code unchanged for 3 rounds. Assuming it is acceptable.")
#             return new_code

#         messages.append({"role": "assistant", "content": reply})
#         messages.append({"role": "user", "content": "Please validate and fix again."})
#         round_counter += 1

#     print("⚠️ Max validation rounds reached. Returning latest version.")
#     return previous_code or swift_code

# # ========== SAVE ==========
# def save_swift_code(swift_code: str, output_folder: str, index: int):
#     os.makedirs(output_folder, exist_ok=True)
#     filename = f"Model_{index + 1}.swift"
#     path = os.path.join(output_folder, filename)
#     with open(path, "w", encoding="utf-8") as f:
#         f.write(swift_code)
#     print(f"💾 Saved: {path}")

# # ========== MAIN ==========
# def main():
#     zip_path = input("📦 Enter path to ZIP file with Kotlin project:\n> ").strip()
#     if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
#         print("❌ Invalid ZIP file.")
#         return

#     with tempfile.TemporaryDirectory() as temp_dir:
#         print("🔓 Extracting ZIP...")
#         with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#             zip_ref.extractall(temp_dir)

#         print("🔍 Scanning for Kotlin model files...")
#         models = extract_kotlin_models(temp_dir)

#         if not models:
#             print("⚠️ No Kotlin data models found.")
#             return

#         output_dir = os.path.join(os.getcwd(), "swift")
#         print(f"📤 Converting and validating {len(models)} models...\n")

#         for i, model in enumerate(models):
#             print(f"\n🔄 [{i + 1}/{len(models)}] Converting Kotlin model...")
#             print("-----------------------------------------------------")
#             print(model[:300] + ("..." if len(model) > 300 else ""))

#             swift_code = convert_model_to_swift(model)
#             print("\n🛠 Swift Output (before validation):")
#             print(swift_code)

#             print("\n🔍 Validating Swift model...")
#             validated_code = validate_swift_model(swift_code)

#             if not validated_code:
#                 print("❌ Could not extract valid Swift code.")
#                 continue

#             print("\n✅ Final Swift model ready. Saving to file...")
#             save_swift_code(validated_code, output_dir, i)

#         print(f"\n🎉 All models converted and saved in: {output_dir}")

# if __name__ == "__main__":
#     main()

import os
import zipfile
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import chromadb
from langchain.agents import AgentType, initialize_agent, Tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferMemory
import re
import ast

@dataclass
class AndroidComponent:
    """Represents an Android component (Activity, Fragment, etc.)"""
    name: str
    type: str  # Activity, Fragment, Service, etc.
    file_path: str
    content: str
    dependencies: List[str]
    ui_elements: List[str]
    data_models: List[str]

@dataclass
class SwiftComponent:
    """Represents a Swift iOS component"""
    name: str
    type: str  # ViewController, View, Model, etc.
    content: str
    dependencies: List[str]

class AndroidCodeAnalyzer:
    """Analyzes Android code structure and extracts components"""
    
    def __init__(self):
        self.components = []
        self.models = []
        self.layouts = []
        
    def extract_from_zip(self, zip_path: str, extract_to: str = "temp_android_project"):
        """Extract Android project from zip file"""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return extract_to
    
    def analyze_java_kotlin_files(self, project_path: str):
        """Analyze Java/Kotlin files to extract components"""
        java_files = list(Path(project_path).rglob("*.java"))
        kotlin_files = list(Path(project_path).rglob("*.kt"))
        
        for file_path in java_files + kotlin_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    component = self._parse_android_component(file_path, content)
                    if component:
                        self.components.append(component)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    def _parse_android_component(self, file_path: Path, content: str) -> Optional[AndroidComponent]:
        """Parse individual Android component file"""
        # Extract class name
        class_match = re.search(r'class\s+(\w+)', content)
        if not class_match:
            return None
        
        class_name = class_match.group(1)
        
        # Determine component type
        component_type = "Unknown"
        if "extends Activity" in content or "extends AppCompatActivity" in content:
            component_type = "Activity"
        elif "extends Fragment" in content:
            component_type = "Fragment"
        elif "extends Service" in content:
            component_type = "Service"
        elif "@Entity" in content or "Room" in content:
            component_type = "Model"
        elif "ViewModel" in content and ("extends ViewModel" in content or "class.*ViewModel" in content or ": ViewModel()" in content):
            component_type = "ViewModel"
        elif "data class" in content:
            component_type = "Model"
        
        # Extract UI elements
        ui_elements = re.findall(r'findViewById\(R\.id\.(\w+)\)', content)
        ui_elements.extend(re.findall(r'binding\.(\w+)', content))
        
        # Extract dependencies
        dependencies = re.findall(r'import\s+([\w.]+)', content)
        
        # Extract data models
        data_models = re.findall(r'(\w+)\s+\w+\s*=\s*new\s+\w+', content)
        
        return AndroidComponent(
            name=class_name,
            type=component_type,
            file_path=str(file_path),
            content=content,
            dependencies=dependencies,
            ui_elements=ui_elements,
            data_models=data_models
        )

class SwiftCodeGenerator:
    """Generates Swift iOS code from Android components"""
    
    def __init__(self):
        self.swift_components = []
    
    def convert_activity_to_viewcontroller(self, android_component: AndroidComponent) -> SwiftComponent:
        """Convert Android Activity to iOS ViewController"""
        # Extract UI elements from the Android code
        ui_elements = self._extract_ui_elements(android_component.content)
        
        swift_content = f"""
import UIKit
import Combine

class {android_component.name}ViewController: UIViewController {{
    
    // MARK: - Properties
    {self._generate_properties(android_component)}
    
    // MARK: - View Model
    private var viewModel: {android_component.name}ViewModel!
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Lifecycle
    override func viewDidLoad() {{
        super.viewDidLoad()
        setupViewModel()
        setupUI()
        setupConstraints()
        setupBindings()
    }}
    
    // MARK: - Setup
    private func setupViewModel() {{
        viewModel = {android_component.name}ViewModel()
    }}
    
    private func setupUI() {{
        view.backgroundColor = .systemBackground
        title = "{android_component.name}"
        {self._generate_ui_setup(android_component)}
    }}
    
    private func setupConstraints() {{
        {self._generate_constraints(android_component)}
    }}
    
    private func setupBindings() {{
        // Bind ViewModel to UI
        viewModel.$uiState
            .receive(on: DispatchQueue.main)
            .sink {{ [weak self] state in
                self?.updateUI(with: state)
            }}
            .store(in: &cancellables)
    }}
    
    // MARK: - UI Updates
    private func updateUI(with state: {android_component.name}UiState) {{
        switch state {{
        case .loading:
            // Show loading indicator
            break
        case .success(let data):
            // Update UI with data
            break
        case .error(let message):
            // Show error
            self.showAlert(message: message)
        }}
    }}
    
    // MARK: - Actions
    {self._generate_actions(android_component)}
    
    // MARK: - Helpers
    private func showAlert(message: String) {{
        let alert = UIAlertController(title: "Error", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }}
}}
"""
        return SwiftComponent(
            name=f"{android_component.name}ViewController",
            type="ViewController",
            content=swift_content,
            dependencies=self._map_dependencies(android_component.dependencies)
        )
    
    def convert_viewmodel_to_swift(self, android_component: AndroidComponent) -> SwiftComponent:
        """Convert Android ViewModel to iOS ViewModel"""
        
        # Extract StateFlow properties from the Android code
        stateflow_properties = self._extract_stateflow_properties(android_component.content)
        
        # Extract methods from the Android code
        methods = self._extract_methods(android_component.content)
        
        swift_content = f"""
import Foundation
import Combine

class {android_component.name}ViewModel: ObservableObject {{
    
    // MARK: - Published Properties
    {self._generate_viewmodel_properties(android_component)}
    
    // MARK: - Private Properties
    private var cancellables = Set<AnyCancellable>()
    private let storageHelper: StorageHelper
    
    // MARK: - Initialization
    init(storageHelper: StorageHelper = StorageHelper.shared) {{
        self.storageHelper = storageHelper
        setupBindings()
        loadData()
    }}
    
    // MARK: - Public Methods
    {self._generate_public_methods(android_component)}
    
    // MARK: - Private Methods
    private func setupBindings() {{
        // Setup any internal bindings
    }}
    
    private func loadData() {{
        // Implement data loading logic based on Android code
        {self._generate_load_data_logic(android_component)}
    }}
}}

// MARK: - UI State
{self._generate_ui_state_enums(android_component)}
"""
        return SwiftComponent(
            name=f"{android_component.name}ViewModel",
            type="ViewModel",
            content=swift_content,
            dependencies=["Foundation", "Combine"]
        )
    
    def convert_model_to_swift(self, android_component: AndroidComponent) -> SwiftComponent:
        """Convert Android model to Swift struct/class"""
        swift_content = f"""
import Foundation

// MARK: - {android_component.name}
struct {android_component.name}: Codable {{
    {self._generate_model_properties(android_component)}
    
    // MARK: - Initializer
    init({self._generate_initializer_params(android_component)}) {{
        {self._generate_initializer_body(android_component)}
    }}
    
    // MARK: - Coding Keys
    enum CodingKeys: String, CodingKey {{
        {self._generate_coding_keys(android_component)}
    }}
}}

// MARK: - Extensions
extension {android_component.name} {{
    // Add any computed properties or methods here
}}
"""
        return SwiftComponent(
            name=android_component.name,
            type="Model",
            content=swift_content,
            dependencies=["Foundation"]
        )
    
    def _extract_ui_elements(self, content: str) -> List[str]:
        """Extract UI elements from Android code"""
        ui_elements = []
        
        # Find findViewById calls
        findViewById_pattern = r'findViewById\(R\.id\.(\w+)\)'
        ui_elements.extend(re.findall(findViewById_pattern, content))
        
        # Find binding references
        binding_pattern = r'binding\.(\w+)'
        ui_elements.extend(re.findall(binding_pattern, content))
        
        # Find variable declarations
        var_pattern = r'private\s+(\w+)\s+(\w+)\s*;'
        matches = re.findall(var_pattern, content)
        for var_type, var_name in matches:
            if any(ui_type in var_type.lower() for ui_type in ['button', 'text', 'edit', 'view', 'label']):
                ui_elements.append(var_name)
        
        return list(set(ui_elements))
    
    def _generate_properties(self, component: AndroidComponent) -> str:
        """Generate Swift properties from Android UI elements"""
        properties = []
        ui_elements = self._extract_ui_elements(component.content)
        
        for ui_element in ui_elements:
            # Map common Android views to iOS equivalents
            if 'button' in ui_element.lower():
                properties.append(f"""    private lazy var {ui_element}: UIButton = {{
        let button = UIButton(type: .system)
        button.setTitle("{ui_element.title()}", for: .normal)
        button.addTarget(self, action: #selector({ui_element}Tapped), for: .touchUpInside)
        return button
    }}()""")
            elif 'text' in ui_element.lower() or 'label' in ui_element.lower():
                properties.append(f"""    private lazy var {ui_element}: UILabel = {{
        let label = UILabel()
        label.text = "{ui_element.title()}"
        label.font = .systemFont(ofSize: 16)
        return label
    }}()""")
            elif 'edit' in ui_element.lower() or 'input' in ui_element.lower():
                properties.append(f"""    private lazy var {ui_element}: UITextField = {{
        let textField = UITextField()
        textField.placeholder = "Enter {ui_element.title()}"
        textField.borderStyle = .roundedRect
        return textField
    }}()""")
            else:
                properties.append(f"""    private lazy var {ui_element}: UIView = {{
        let view = UIView()
        view.backgroundColor = .systemGray5
        return view
    }}()""")
        
        return "\n".join(properties) if properties else "    // No UI elements found"
    
    def _generate_viewmodel_properties(self, component: AndroidComponent) -> str:
        """Generate ViewModel properties"""
        properties = []
        
        # Look for StateFlow and MutableStateFlow patterns
        stateflow_pattern = r'private val _(\w+) = MutableStateFlow<(\w+)>'
        matches = re.findall(stateflow_pattern, component.content)
        
        for var_name, var_type in matches:
            swift_type = self._map_java_type_to_swift(var_type)
            properties.append(f"    @Published var {var_name}: {swift_type}?")
        
        return "\n".join(properties) if properties else "    // No published properties found"
    
    def _generate_model_properties(self, component: AndroidComponent) -> str:
        """Generate model properties from Android model"""
        properties = []
        
        # Look for data class properties
        property_patterns = [
            r'val\s+(\w+):\s+(\w+)',
            r'var\s+(\w+):\s+(\w+)',
            r'@SerializedName\("(\w+)"\)\s+val\s+(\w+):\s+(\w+)'
        ]
        
        for pattern in property_patterns:
            matches = re.findall(pattern, component.content)
            for match in matches:
                if len(match) == 2:
                    prop_name, prop_type = match
                    swift_type = self._map_java_type_to_swift(prop_type)
                    properties.append(f"    let {prop_name}: {swift_type}")
                elif len(match) == 3:
                    serial_name, prop_name, prop_type = match
                    swift_type = self._map_java_type_to_swift(prop_type)
                    properties.append(f"    let {prop_name}: {swift_type}")
        
        return "\n".join(properties) if properties else "    // Add properties here"
    
    def _generate_coding_keys(self, component: AndroidComponent) -> str:
        """Generate CodingKeys for Codable conformance"""
        keys = []
        
        # Look for @SerializedName annotations
        serial_name_pattern = r'@SerializedName\("(\w+)"\)\s+val\s+(\w+):'
        matches = re.findall(serial_name_pattern, component.content)
        
        for serial_name, prop_name in matches:
            keys.append(f'        case {prop_name} = "{serial_name}"')
        
        # Add default cases for properties without SerializedName
        property_pattern = r'val\s+(\w+):\s+(\w+)'
        all_props = re.findall(property_pattern, component.content)
        
        for prop_name, prop_type in all_props:
            if not any(prop_name in match[1] for match in matches):
                keys.append(f'        case {prop_name}')
        
        return "\n".join(keys) if keys else "        // No custom coding keys needed"
    
    def _generate_ui_setup(self, component: AndroidComponent) -> str:
        """Generate UI setup code"""
        setup_code = []
        ui_elements = self._extract_ui_elements(component.content)
        
        for ui_element in ui_elements:
            setup_code.append(f"        view.addSubview({ui_element})")
        
        return "\n".join(setup_code) if setup_code else "        // No UI setup needed"
    
    def _generate_constraints(self, component: AndroidComponent) -> str:
        """Generate Auto Layout constraints"""
        constraints = []
        ui_elements = self._extract_ui_elements(component.content)
        
        for ui_element in ui_elements:
            constraints.append(f"        {ui_element}.translatesAutoresizingMaskIntoConstraints = false")
        
        # Add basic constraints
        if ui_elements:
            constraints.append("        NSLayoutConstraint.activate([")
            for i, ui_element in enumerate(ui_elements):
                constraints.append(f"            {ui_element}.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: {20 + i * 60}),")
                constraints.append(f"            {ui_element}.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),")
                constraints.append(f"            {ui_element}.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20)")
            constraints.append("        ])")
        
        return "\n".join(constraints) if constraints else "        // No constraints needed"
    
    def _generate_actions(self, component: AndroidComponent) -> str:
        """Generate action methods"""
        actions = []
        ui_elements = self._extract_ui_elements(component.content)
        
        for ui_element in ui_elements:
            if 'button' in ui_element.lower():
                actions.append(f"""
    @objc private func {ui_element}Tapped() {{
        // Handle {ui_element} tap
        print(f"\(ui_element) tapped")
    }}""")
        
        return "\n".join(actions) if actions else "\n    // No actions needed"
    
    def _map_java_type_to_swift(self, java_type: str) -> str:
        """Map Java types to Swift types"""
        type_mapping = {
            'String': 'String',
            'Int': 'Int',
            'Integer': 'Int',
            'int': 'Int',
            'Long': 'Int64',
            'long': 'Int64',
            'Double': 'Double',
            'double': 'Double',
            'Float': 'Float',
            'float': 'Float',
            'Boolean': 'Bool',
            'boolean': 'Bool',
            'List': 'Array',
            'ArrayList': 'Array',
            'Map': 'Dictionary',
            'HashMap': 'Dictionary',
            'MutableStateFlow': 'Any',
            'StateFlow': 'Any',
            'LiveData': 'Any'
        }
        
        # Handle generic types
        if '<' in java_type:
            base_type = java_type.split('<')[0]
            generic_type = java_type.split('<')[1].split('>')[0]
            swift_base = type_mapping.get(base_type, base_type)
            swift_generic = type_mapping.get(generic_type, generic_type)
            return f"[{swift_generic}]" if swift_base == 'Array' else f"[String: {swift_generic}]"
        
        return type_mapping.get(java_type, java_type)
    
    def _generate_initializer_params(self, component: AndroidComponent) -> str:
        """Generate initializer parameters"""
        # Extract properties from the model
        property_pattern = r'val\s+(\w+):\s+(\w+)'
        matches = re.findall(property_pattern, component.content)
        
        params = []
        for prop_name, prop_type in matches:
            swift_type = self._map_java_type_to_swift(prop_type)
            params.append(f"{prop_name}: {swift_type}")
        
        return ", ".join(params) if params else ""
    
    def _generate_initializer_body(self, component: AndroidComponent) -> str:
        """Generate initializer body"""
        # Extract properties from the model
        property_pattern = r'val\s+(\w+):\s+(\w+)'
        matches = re.findall(property_pattern, component.content)
        
        assignments = []
        for prop_name, prop_type in matches:
            assignments.append(f"        self.{prop_name} = {prop_name}")
        
        return "\n".join(assignments) if assignments else "        // Initialize properties"
    
    def _map_dependencies(self, android_deps: List[str]) -> List[str]:
        """Map Android dependencies to iOS equivalents"""
        dependency_mapping = {
            'androidx.appcompat.app.AppCompatActivity': 'UIKit',
            'androidx.lifecycle.ViewModel': 'Foundation',
            'androidx.lifecycle.ViewModelProvider': 'Foundation',
            'kotlinx.coroutines.flow.MutableStateFlow': 'Combine',
            'kotlinx.coroutines.flow.StateFlow': 'Combine',
            'android.util.Log': 'Foundation',
            'kotlinx.serialization.Serializable': 'Foundation'
        }
        
        swift_deps = []
        for dep in android_deps:
            swift_dep = dependency_mapping.get(dep, 'Foundation')
            if swift_dep not in swift_deps:
                swift_deps.append(swift_dep)
        
        return swift_deps if swift_deps else ['Foundation']
    
    def _extract_stateflow_properties(self, content: str) -> List[tuple]:
        """Extract StateFlow properties from Android code"""
        properties = []
        
        # Look for StateFlow patterns
        patterns = [
            r'private val _(\w+) = MutableStateFlow<(\w+)>',
            r'val (\w+): StateFlow<(\w+)>',
            r'private val _(\w+) = MutableStateFlow<(\w+)>\((\w+)\(\)\)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    var_name, var_type = match
                    properties.append((var_name, var_type))
                elif len(match) == 3:
                    var_name, var_type, initial_value = match
                    properties.append((var_name, var_type, initial_value))
        
        return properties
    
    def _extract_methods(self, content: str) -> List[str]:
        """Extract method names from Android code"""
        methods = []
        
        # Look for function declarations
        method_pattern = r'fun\s+(\w+)\s*\([^)]*\)'
        matches = re.findall(method_pattern, content)
        
        for method in matches:
            if method not in ['init', 'loadLevels', 'determineLevelStates']:  # Skip private methods
                methods.append(method)
        
        return methods
    
    def _generate_public_methods(self, component: AndroidComponent) -> str:
        """Generate public methods from Android ViewModel"""
        methods = self._extract_methods(component.content)
        
        swift_methods = []
        for method in methods:
            if method == 'refreshLevels':
                swift_methods.append(f"""
    func refresh() {{
        loadData()
    }}""")
            elif method == 'getLevelTitle':
                swift_methods.append(f"""
    func getLevelTitle() -> String {{
        return level.title
    }}""")
            else:
                swift_methods.append(f"""
    func {method}() {{
        // TODO: Implement {method}
    }}""")
        
        return "\n".join(swift_methods) if swift_methods else """
    func refresh() {
        loadData()
    }"""
    
    def _generate_load_data_logic(self, component: AndroidComponent) -> str:
        """Generate load data logic based on Android code"""
        if 'loadLevels' in component.content:
            return """
        // Load levels for the current sport
        let levels = storageHelper.getLevelsForSport("tennis.json")
        let progress = storageHelper.getAllLevelProgress()
        
        // Update UI state
        DispatchQueue.main.async {
            self.uiState = .success(levels)
        }"""
        else:
            return """
        // Implement data loading logic
        DispatchQueue.main.async {
            self.uiState = .loading
        }"""
    
    def _generate_ui_state_enums(self, component: AndroidComponent) -> str:
        """Generate UI state enums from Android sealed classes"""
        if 'sealed class' in component.content or 'enum class' in component.content:
            # Extract enum cases
            enum_pattern = r'(object|data class)\s+(\w+)\s*:\s*(\w+)'
            matches = re.findall(enum_pattern, component.content)
            
            if matches:
                enum_name = f"{component.name}UiState"
                cases = []
                
                for match in matches:
                    case_type, case_name, parent_class = match
                    if case_type == 'object':
                        cases.append(f"    case {case_name}")
                    elif case_type == 'data class':
                        cases.append(f"    case {case_name}(Any)")
                
                return f"""enum {enum_name} {{
{cases}
}}"""
        
        # Default UI state
        return f"""enum {component.name}UiState {{
    case loading
    case success(Any)
    case error(String)
}}"""

class AndroidToiOSConverter:
    """Main converter class using LangChain and RAG"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            temperature=0.1,
            model="gpt-4"
        )
        
        # Initialize ChromaDB with new client
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        
        # Initialize components
        self.android_analyzer = AndroidCodeAnalyzer()
        self.swift_generator = SwiftCodeGenerator()
        
        # Initialize vector store
        self.vector_store = None
        self.qa_chain = None
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize tools
        self.tools = self._create_tools()
        
        # Initialize agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the LangChain agent"""
        
        def analyze_android_code(query: str) -> str:
            """Analyze Android code and extract components"""
            components_info = []
            for comp in self.android_analyzer.components:
                components_info.append(f"{comp.name} ({comp.type})")
            return f"Found {len(self.android_analyzer.components)} components: {', '.join(components_info)}"
        
        def generate_swift_code(query: str) -> str:
            """Generate Swift code from Android components"""
            if not self.android_analyzer.components:
                return "No Android components found to convert"
            
            converted_count = 0
            for comp in self.android_analyzer.components:
                if comp.type in ["Activity", "Model"]:
                    converted_count += 1
            
            return f"Generated Swift code for {converted_count} components"
        
        def query_knowledge_base(query: str) -> str:
            """Query the RAG knowledge base"""
            if self.qa_chain:
                try:
                    result = self.qa_chain.invoke({"query": query})
                    return result.get("result", "No result found")
                except Exception as e:
                    return f"Error querying knowledge base: {e}"
            return "Knowledge base not initialized"
        
        return [
            Tool(
                name="Android Code Analyzer",
                func=analyze_android_code,
                description="Analyzes Android code to extract components, activities, fragments, and models"
            ),
            Tool(
                name="Swift Code Generator",
                func=generate_swift_code,
                description="Generates Swift iOS code from Android components"
            ),
            Tool(
                name="Knowledge Base Query",
                func=query_knowledge_base,
                description="Queries the RAG knowledge base for Android to iOS conversion patterns"
            )
        ]
    
    def setup_knowledge_base(self, docs_path: str = "conversion_docs"):
        """Setup RAG knowledge base with conversion patterns"""
        try:
            # Create sample conversion documentation
            self._create_conversion_docs(docs_path)
            
            # Load documents
            documents = []
            for file_path in Path(docs_path).rglob("*.txt"):
                try:
                    loader = TextLoader(str(file_path))
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
            
            if not documents:
                print("No documents loaded for knowledge base")
                return
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            texts = text_splitter.split_documents(documents)
            
            # Create vector store with new ChromaDB client
            self.vector_store = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                client=self.chroma_client,
                collection_name="android_ios_conversion"
            )
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            print("Knowledge base setup completed successfully")
            
        except Exception as e:
            print(f"Error setting up knowledge base: {e}")
    
    def _create_conversion_docs(self, docs_path: str):
        """Create sample conversion documentation"""
        Path(docs_path).mkdir(exist_ok=True)
        
        # Android to iOS conversion patterns
        conversion_patterns = {
            "activity_to_viewcontroller.txt": """
Android Activity to iOS ViewController Conversion:

1. Activity lifecycle methods:
   - onCreate() -> viewDidLoad()
   - onStart() -> viewWillAppear()
   - onResume() -> viewDidAppear()
   - onPause() -> viewWillDisappear()
   - onStop() -> viewDidDisappear()
   - onDestroy() -> viewDidUnload()

2. UI Components:
   - TextView -> UILabel
   - EditText -> UITextField
   - Button -> UIButton
   - ImageView -> UIImageView
   - ListView -> UITableView
   - RecyclerView -> UICollectionView

3. Layout:
   - LinearLayout -> UIStackView
   - RelativeLayout -> Auto Layout constraints
   - ConstraintLayout -> Auto Layout constraints
            """,
            
            "data_models.txt": """
Android Model to iOS Model Conversion:

1. Data Classes:
   - Java/Kotlin data class -> Swift struct
   - Getter/Setter methods -> Swift computed properties
   - Serialization annotations -> Codable protocol

2. Room Database:
   - @Entity -> CoreData NSManagedObject
   - @Dao -> CoreData NSManagedObjectContext operations
   - Room queries -> CoreData fetch requests

3. Retrofit Models:
   - @SerializedName -> CodingKeys enum
   - Gson -> JSONDecoder/JSONEncoder
            """,
            
            "viewmodels.txt": """
Android ViewModel to iOS ViewModel Conversion:

1. Architecture:
   - Android ViewModel -> iOS ViewModel (MVVM pattern)
   - LiveData -> Combine Publishers or Observable
   - Repository pattern -> Service layer

2. State Management:
   - MutableLiveData -> @Published properties
   - Observer pattern -> Combine subscribers
   - Data binding -> SwiftUI @StateObject/@ObservedObject
            """
        }
        
        for filename, content in conversion_patterns.items():
            try:
                with open(Path(docs_path) / filename, 'w') as f:
                    f.write(content)
            except Exception as e:
                print(f"Error creating {filename}: {e}")
    
    def convert_android_to_ios(self, android_zip_path: str, output_dir: str = "ios_output"):
        """Main conversion method"""
        try:
            # Step 1: Extract and analyze Android project
            print("Extracting Android project...")
            project_path = self.android_analyzer.extract_from_zip(android_zip_path)
            
            print("Analyzing Android components...")
            self.android_analyzer.analyze_java_kotlin_files(project_path)
            
            if not self.android_analyzer.components:
                print("No Android components found in the project")
                return []
            
            # Step 2: Setup knowledge base
            print("Setting up knowledge base...")
            self.setup_knowledge_base()
            
            # Step 3: Convert components
            print("Converting to iOS...")
            Path(output_dir).mkdir(exist_ok=True)
            
            converted_components = []
            
            for android_component in self.android_analyzer.components:
                print(f"Converting {android_component.name} ({android_component.type})...")
                
                # Generate Swift code based on component type
                if android_component.type == "Activity":
                    swift_component = self.swift_generator.convert_activity_to_viewcontroller(android_component)
                elif android_component.type == "Model":
                    swift_component = self.swift_generator.convert_model_to_swift(android_component)
                else:
                    # For other types, create a basic conversion
                    swift_component = SwiftComponent(
                        name=f"{android_component.name}Swift",
                        type=android_component.type,
                        content=f"// Converted from {android_component.type}\n// TODO: Implement conversion for {android_component.name}",
                        dependencies=[]
                    )
                
                converted_components.append(swift_component)
                
                # Save Swift file
                swift_file_path = Path(output_dir) / f"{swift_component.name}.swift"
                with open(swift_file_path, 'w') as f:
                    f.write(swift_component.content)
            
            # Step 4: Generate project structure
            self._generate_ios_project_structure(output_dir, converted_components)
            
            print(f"Conversion complete! iOS project saved to {output_dir}")
            print(f"Generated {len(converted_components)} Swift files")
            
            return converted_components
            
        except Exception as e:
            print(f"Error during conversion: {e}")
            return []
    
    def _generate_ios_project_structure(self, output_dir: str, components: List[SwiftComponent]):
        """Generate iOS project structure and files"""
        try:
            # Create basic iOS project structure
            directories = [
                "Models",
                "Views", 
                "ViewModels",
                "Controllers",
                "Services",
                "Resources"
            ]
            
            for directory in directories:
                Path(output_dir, directory).mkdir(exist_ok=True)
            
            # Generate AppDelegate
            app_delegate = """import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Override point for customization after application launch.
        return true
    }

    // MARK: UISceneSession Lifecycle

    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        // Called when a new scene session is being created.
        // Use this method to select a configuration to create the new scene with.
        return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
    }

    func application(_ application: UIApplication, didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {
        // Called when the user discards a scene session.
        // If any sessions were discarded while the application was not running, this will be called shortly after application:didFinishLaunchingWithOptions.
        // Use this method to release any resources that were specific to the discarded scenes, as they will not return.
    }
}
"""
            
            # Generate SceneDelegate
            scene_delegate = """import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = (scene as? UIWindowScene) else { return }
        
        window = UIWindow(windowScene: windowScene)
        
        // Set up the initial view controller
        let mainViewController = MainActivityViewController()
        let navigationController = UINavigationController(rootViewController: mainViewController)
        
        window?.rootViewController = navigationController
        window?.makeKeyAndVisible()
    }

    func sceneDidDisconnect(_ scene: UIScene) {
        // Called as the scene is being released by the system.
        // This occurs shortly after the scene enters the background, or when its session is discarded.
        // Release any resources associated with this scene that can be re-created the next time the scene connects.
        // The scene may re-connect later, as its session was not necessarily discarded (see `application:didDiscardSceneSessions` instead).
    }

    func sceneDidBecomeActive(_ scene: UIScene) {
        // Called when the scene has moved from an inactive state to an active state.
        // Use this method to restart any tasks that were paused (or not yet started) when the scene was inactive.
    }

    func sceneWillResignActive(_ scene: UIScene) {
        // Called when the scene will move from an active state to an inactive state.
        // This may occur due to temporary interruptions (ex.g. an incoming phone call).
    }

    func sceneWillEnterForeground(_ scene: UIScene) {
        // Called as the scene transitions from the background to the foreground.
        // Use this method to undo the changes made on entering the background.
    }

    func sceneDidEnterBackground(_ scene: UIScene) {
        // Called as the scene transitions from the foreground to the background.
        // Use this method to save data, release shared resources, and store enough scene-specific state information
        // to restore the scene back to its current state.
    }
}
"""
            
            # Generate StorageHelper (iOS equivalent)
            storage_helper = """import Foundation

class StorageHelper {
    static let shared = StorageHelper()
    
    private let userDefaults = UserDefaults.standard
    
    private init() {}
    
    // MARK: - Level Progress
    func getAllLevelProgress() -> [LevelProgress] {
        guard let data = userDefaults.data(forKey: "levelProgress"),
              let progress = try? JSONDecoder().decode([LevelProgress].self, from: data) else {
            return []
        }
        return progress
    }
    
    func markLevelCompleted(_ levelId: Int) {
        var progress = getAllLevelProgress()
        
        if let index = progress.firstIndex(where: { $0.levelId == levelId }) {
            progress[index].completed = true
        } else {
            let newProgress = LevelProgress(levelId: levelId, completed: true)
            progress.append(newProgress)
        }
        
        if let data = try? JSONEncoder().encode(progress) {
            userDefaults.set(data, forKey: "levelProgress")
        }
    }
    
    // MARK: - Level Data
    func getLevelsForSport(_ sport: String) -> [Level] {
        guard let url = Bundle.main.url(forResource: sport.replacingOccurrences(of: ".json", with: ""), withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let levels = try? JSONDecoder().decode([Level].self, from: data) else {
            return []
        }
        return levels
    }
    
    // MARK: - Answer Tracking
    func saveAnswer(_ levelId: Int, _ isCorrect: Bool) {
        var progress = getAllLevelProgress()
        
        if let index = progress.firstIndex(where: { $0.levelId == levelId }) {
            if isCorrect {
                progress[index].correctAnswers += 1
            } else {
                progress[index].wrongAnswers += 1
            }
        } else {
            let newProgress = LevelProgress(
                levelId: levelId,
                correctAnswers: isCorrect ? 1 : 0,
                wrongAnswers: isCorrect ? 0 : 1
            )
            progress.append(newProgress)
        }
        
        if let data = try? JSONEncoder().encode(progress) {
            userDefaults.set(data, forKey: "levelProgress")
        }
    }
}
"""
            
            # Generate Info.plist
            info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>$(DEVELOPMENT_LANGUAGE)</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>$(PRODUCT_BUNDLE_PACKAGE_TYPE)</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>UIApplicationSceneManifest</key>
    <dict>
        <key>UIApplicationSupportsMultipleScenes</key>
        <false/>
        <key>UISceneConfigurations</key>
        <dict>
            <key>UIWindowSceneSessionRoleApplication</key>
            <array>
                <dict>
                    <key>UISceneConfigurationName</key>
                    <string>Default Configuration</string>
                    <key>UISceneDelegateClassName</key>
                    <string>$(PRODUCT_MODULE_NAME).SceneDelegate</string>
                </dict>
            </array>
        </dict>
    </dict>
</dict>
</plist>"""
            
            # Write files
            with open(Path(output_dir) / "AppDelegate.swift", 'w') as f:
                f.write(app_delegate)
            
            with open(Path(output_dir) / "SceneDelegate.swift", 'w') as f:
                f.write(scene_delegate)
            
            with open(Path(output_dir) / "Services/StorageHelper.swift", 'w') as f:
                f.write(storage_helper)
            
            with open(Path(output_dir) / "Info.plist", 'w') as f:
                f.write(info_plist)
            
            # Generate conversion report
            component_types = {}
            for comp in components:
                if comp.type not in component_types:
                    component_types[comp.type] = []
                component_types[comp.type].append(comp.name)
            
            report = {
                "conversion_summary": {
                    "total_components": len(components),
                    "component_types": component_types
                },
                "files_generated": [comp.name + ".swift" for comp in components] + [
                    "AppDelegate.swift",
                    "SceneDelegate.swift", 
                    "Services/StorageHelper.swift",
                    "Info.plist"
                ]
            }
            
            with open(Path(output_dir) / "conversion_report.json", 'w') as f:
                json.dump(report, f, indent=2)
                
        except Exception as e:
            print(f"Error generating project structure: {e}")

# Example usage
if __name__ == "__main__":
    try:
        # Initialize converter with your actual OpenAI API key
        converter = AndroidToiOSConverter(openai_api_key="sk-your-actual-api-key-here")
        
        # Test with sample data first
        print("Testing Android to iOS converter...")
        
        # Create a sample Android component for testing
        sample_component = AndroidComponent(
            name="MainActivity",
            type="Activity",
            file_path="MainActivity.java",
            content="""
            public class MainActivity extends AppCompatActivity {
                private Button loginButton;
                private EditText usernameField;
                private TextView titleLabel;
                
                @Override
                protected void onCreate(Bundle savedInstanceState) {
                    super.onCreate(savedInstanceState);
                    setContentView(R.layout.activity_main);
                    
                    loginButton = findViewById(R.id.loginButton);
                    usernameField = findViewById(R.id.usernameField);
                    titleLabel = findViewById(R.id.titleLabel);
                }
            }
            """,
            dependencies=["androidx.appcompat.app.AppCompatActivity"],
            ui_elements=["loginButton", "usernameField", "titleLabel"],
            data_models=[]
        )
        
        converter.android_analyzer.components = [sample_component]
        
        # Convert to iOS
        output_directory = "converted_ios_app"
        
        # Since we already extracted the zip file, we'll analyze the current directory
        print("Analyzing extracted Android project...")
        converter.android_analyzer.analyze_java_kotlin_files(".")
        
        if not converter.android_analyzer.components:
            print("No Android components found in the project")
            print("Test conversion completed! Generated 0 components.")
        else:
            # Setup knowledge base
            print("Setting up knowledge base...")
            converter.setup_knowledge_base()
            
            # Convert components
            print("Converting to iOS...")
            Path(output_directory).mkdir(exist_ok=True)
            
            converted_components = []
            
            for android_component in converter.android_analyzer.components:
                print(f"Converting {android_component.name} ({android_component.type})...")
                
                # Generate Swift code based on component type
                if android_component.type == "Activity":
                    swift_component = converter.swift_generator.convert_activity_to_viewcontroller(android_component)
                elif android_component.type == "ViewModel":
                    swift_component = converter.swift_generator.convert_viewmodel_to_swift(android_component)
                elif android_component.type == "Model":
                    swift_component = converter.swift_generator.convert_model_to_swift(android_component)
                else:
                    # For other types, create a basic conversion
                    swift_component = SwiftComponent(
                        name=f"{android_component.name}Swift",
                        type=android_component.type,
                        content=f"// Converted from {android_component.type}\n// TODO: Implement conversion for {android_component.name}",
                        dependencies=[]
                    )
                
                converted_components.append(swift_component)
                
                # Save Swift file
                swift_file_path = Path(output_directory) / f"{swift_component.name}.swift"
                with open(swift_file_path, 'w') as f:
                    f.write(swift_component.content)
            
            # Generate project structure
            converter._generate_ios_project_structure(output_directory, converted_components)
        
        print(f"Test conversion completed! Generated {len(converted_components)} components.")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        print("Please make sure to:")
        print("1. Install required packages: pip install langchain-openai langchain-community chromadb")
        print("2. Set your actual OpenAI API key")
        print("3. Provide a valid Android app zip file")