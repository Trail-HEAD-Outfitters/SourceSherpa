"""
Loads pattern definitions into the 'patterns' collection in MongoDB.
Call this after changing patterns or on first project setup.
"""

import json
from pymongo import MongoClient
import argparse
# MongoDB setup
MONGO_URI = "mongodb://root:password@localhost:27017/"
DB_NAME = "code_routing"
client = MongoClient(MONGO_URI)
db = client["code_routing"]
patterns_col = db["patterns"]

# Inline fallback patterns (customize or externalize as needed)
PATTERNS = [
    {"keyword": "Controller", "file_patterns": ["*Controller.cs"], "directories": ["Controllers/", "*/Controllers/"], "notes": "ASP.NET MVC & Web‑API controllers"},
    {"keyword": "API Controller", "file_patterns": ["*ApiController.cs"], "directories": ["Controllers/Api/"], "notes": "REST endpoints"},
    {"keyword": "Minimal API Endpoint", "file_patterns": ["*Endpoints.cs", "*MinimalApi.cs", "Program.cs"], "directories": ["Root", "Endpoints/"], "notes": ".NET 6+ top‑level HTTP handlers"},
    {"keyword": "Endpoint Group / Module", "file_patterns": ["*EndpointGroup.cs", "*Module.cs"], "directories": ["Endpoints/", "Modules/"], "notes": "Logical grouping for Minimal API"},
    {"keyword": "Razor Page", "file_patterns": ["*.cshtml", "*Page.cshtml.cs"], "directories": ["Pages/", "Areas/*/Pages/"], "notes": "Server‑rendered UI"},
    {"keyword": "View / Partial / Layout", "file_patterns": ["*.cshtml", "_*Partial.cshtml", "_Layout.cshtml"], "directories": ["Views/", "Pages/Shared/"], "notes": "Razor & MVC views"},
    {"keyword": "Blazor Component / Layout", "file_patterns": ["*.razor", "*Layout.razor"], "directories": ["Components/", "Pages/", "Shared/"], "notes": "Blazor WASM / Server components"},
    {"keyword": "Tag Helper / View Component", "file_patterns": ["*TagHelper.cs", "*ViewComponent.cs"], "directories": ["TagHelpers/", "ViewComponents/"], "notes": "Reusable UI helpers"},
    {"keyword": "Service / Manager / Provider", "file_patterns": ["*Service.cs", "*Manager.cs", "*Provider.cs"], "directories": ["Services/", "*/Services/"], "notes": "Business‑logic orchestration"},
    {"keyword": "Hosted Service / Worker", "file_patterns": ["*HostedService.cs", "*Worker.cs", "*BackgroundService.cs"], "directories": ["Workers/", "BackgroundServices/"], "notes": "Long‑running tasks"},
    {"keyword": "Cron / Scheduled Job", "file_patterns": ["*Job.cs", "*Scheduler.cs"], "directories": ["Jobs/", "Scheduling/"], "notes": "Quartz, Hangfire, etc."},
    {"keyword": "Repository", "file_patterns": ["*Repository.cs"], "directories": ["Repositories/"], "notes": "Data‑access layer"},
    {"keyword": "Unit of Work", "file_patterns": ["*UnitOfWork.cs"], "directories": ["Infrastructure/UnitOfWork/"], "notes": "Transaction wrapper"},
    {"keyword": "DbContext", "file_patterns": ["*Context.cs", "*DbContext.cs"], "directories": ["Data/", "Persistence/"], "notes": "EF Core context"},
    {"keyword": "Migration (EF Core)", "file_patterns": ["*Migration.cs"], "directories": ["Migrations/", "Database/Migrations/"], "notes": "Code‑based DB migrations"},
    {"keyword": "EntityType Configuration", "file_patterns": ["*Configuration.cs"], "directories": ["Data/Configurations/", "Mappings/"], "notes": "Fluent‑API mapping classes"},
    {"keyword": "Specification (DDD)", "file_patterns": ["*Specification.cs", "*Spec.cs"], "directories": ["Specifications/"], "notes": "Query predicates (Ardalis)"},
    {"keyword": "DTO / Contract / Request", "file_patterns": ["*Dto.cs", "*Request.cs", "*Response.cs"], "directories": ["DTOs/", "Contracts/"], "notes": "Data‑transfer objects"},
    {"keyword": "Model / Entity / Record", "file_patterns": ["*Model.cs", "*Entity.cs", "*Record.cs"], "directories": ["Models/", "Domain/Models/"], "notes": "Domain objects"},
    {"keyword": "ViewModel", "file_patterns": ["*ViewModel.cs"], "directories": ["ViewModels/"], "notes": "MVVM pattern"},
    {"keyword": "Validator (FluentValidation)", "file_patterns": ["*Validator.cs"], "directories": ["Validators/"], "notes": "Request / domain validation"},
    {"keyword": "Mediator Command / Query", "file_patterns": ["*Command.cs", "*Query.cs", "*Handler.cs"], "directories": ["Application/Commands/", "Handlers/"], "notes": "CQRS with MediatR"},
    {"keyword": "Message Consumer / Producer", "file_patterns": ["*Consumer.cs", "*Producer.cs"], "directories": ["Messaging/", "Bus/"], "notes": "MassTransit, Kafka, etc."},
    {"keyword": "Event / Domain Event", "file_patterns": ["*Event.cs", "*Message.cs"], "directories": ["Events/"], "notes": "Publish‑subscribe"},
    {"keyword": "SignalR Hub", "file_patterns": ["*Hub.cs"], "directories": ["Hubs/", "SignalR/"], "notes": "Real‑time websockets"},
    {"keyword": "AutoMapper Profile", "file_patterns": ["*Profile.cs"], "directories": ["Mapping/", "Profiles/"], "notes": "Mapping definitions"},
    {"keyword": "Mapper Extensions", "file_patterns": ["*MappingExtensions.cs"], "directories": ["Extensions/"], "notes": "Static helper methods"},
    {"keyword": "Options / Settings Class", "file_patterns": ["*Options.cs", "*Settings.cs"], "directories": ["Options/", "Config/"], "notes": "Strong‑typed config"},
    {"keyword": "Configuration Files", "file_patterns": ["appsettings.json", "web.config", "*.config"], "directories": ["Root", "Config/"], "notes": "Environment & secrets"},
    {"keyword": "Policy / Authorization Handler", "file_patterns": ["*Policy.cs", "*AuthorizationHandler.cs"], "directories": ["Policies/", "Authorization/"], "notes": "Role/resource rules"},
    {"keyword": "Middleware", "file_patterns": ["*Middleware.cs"], "directories": ["Middleware/"], "notes": "ASP.NET Core pipeline"},
    {"keyword": "Filter (MVC)", "file_patterns": ["*Filter.cs"], "directories": ["Filters/"], "notes": "Action & exception filters"},
    {"keyword": "Health Check", "file_patterns": ["*HealthCheck.cs"], "directories": ["HealthChecks/"], "notes": "Liveness probes"},
    {"keyword": "Caching Policy / Extension", "file_patterns": ["*CachePolicy.cs"], "directories": ["Caching/"], "notes": "In‑memory / distributed caching"},
    {"keyword": "OpenAPI / Swagger Config", "file_patterns": ["SwaggerConfig.cs", "*OpenApi.cs"], "directories": ["Infrastructure/OpenApi/"], "notes": "Swashbuckle, NSwag setup"},
    {"keyword": "Telemetry / OpenTelemetry", "file_patterns": ["*Telemetry.cs", "*Tracing.cs"], "directories": ["Observability/"], "notes": "Distributed tracing"},
    {"keyword": "Enum", "file_patterns": ["*Enum.cs"], "directories": ["Enums/"], "notes": "Enumeration definitions"},
    {"keyword": "Logger / Logging", "file_patterns": ["*Logger.cs", "*Log.cs"], "directories": ["Logging/"], "notes": "Log sinks & wrappers"},
    {"keyword": "Startup / Entry‑Point", "file_patterns": ["Program.cs", "Startup.cs", "App.xaml"], "directories": ["Root", "src/"], "notes": "Hosts & bootstrapping"},
    {"keyword": "Build / CI", "file_patterns": [".yml", ".yaml", "*.cake", "*.ps1"], "directories": [".github/workflows/", "build/"], "notes": "Pipelines & scripts"},
    {"keyword": "Unit Test", "file_patterns": ["*Test.cs", "*Tests.cs"], "directories": ["Tests/"], "notes": "xUnit, NUnit, MSTest"},
    {"keyword": "Integration Test", "file_patterns": ["*IntegrationTest.cs"], "directories": ["IntegrationTests/"], "notes": "End‑to‑end tests"},
    {"keyword": "Solution File", "file_patterns": ["*.sln"], "directories": ["Root"], "notes": "Visual Studio solution"},
    {"keyword": "Project File", "file_patterns": ["*.csproj", "*.fsproj"], "directories": ["Root", "src/"], "notes": "SDK & legacy projects"},
    {"keyword": "Feature Folder", "file_patterns": [], "directories": ["Features/<FeatureName>/"], "notes": "Vertical slice structure"},
    {"keyword": "Solution Filter", "file_patterns": ["*.slnf"], "directories": ["Root"], "notes": "Filtered solution"},
    {"keyword": "Directory.Build.props / targets", "file_patterns": ["Directory.Build.props", "Directory.Build.targets"], "directories": ["Solution root"], "notes": "Centralised MSBuild"},
    {"keyword": "React Component", "file_patterns": ["*.tsx", "*.jsx"], "directories": ["ClientApp/src/components/", "react-app/src/"], "notes": "Functional/class components"},
    {"keyword": "React Hook", "file_patterns": ["use*.ts", "use*.js"], "directories": ["ClientApp/src/hooks/"], "notes": "Custom hooks"},
    {"keyword": "Redux Slice / Store", "file_patterns": ["*.slice.ts", "store.ts"], "directories": ["ClientApp/src/store/"], "notes": "State management"},
    {"keyword": "AngularJS Controller", "file_patterns": ["*.controller.js", "*.controller.ts"], "directories": ["ClientApp/app/", "angularjs/"], "notes": "Angular 1.x controllers"},
    {"keyword": "AngularJS Service / Factory", "file_patterns": ["*.service.js", "*.factory.js"], "directories": ["ClientApp/app/", "angularjs/"], "notes": "DI services"},
    {"keyword": "AngularJS Directive", "file_patterns": ["*.directive.js"], "directories": ["ClientApp/app/"], "notes": "Reusable UI directive"},
    {"keyword": "SQL Stored Procedure", "file_patterns": ["*.sql", "*Proc.sql", "sp*.sql"], "directories": ["Database/Scripts/StoredProcs/", "Sql/"], "notes": "T‑SQL stored procs"},
    {"keyword": "SQL View", "file_patterns": ["vw*.sql"], "directories": ["Database/Scripts/Views/"], "notes": "Indexed / select views"},
    {"keyword": "SQL Table / Schema", "file_patterns": ["tbl*.sql", "*.ddl.sql"], "directories": ["Database/Scripts/Tables/"], "notes": "DDL scripts"},
    {"keyword": "SQL Function", "file_patterns": ["fn*.sql"], "directories": ["Database/Scripts/Functions/"], "notes": "Scalar / table functions"},
    {"keyword": "Data Seed / Seed Script", "file_patterns": ["Seed*.sql", "*SeedData.cs"], "directories": ["Database/Seed/", "Data/Seed/"], "notes": "Initial data load"},
    {"keyword": "SSIS Package", "file_patterns": ["*.dtsx"], "directories": ["SSIS/", "ETL/"], "notes": "SQL Server Integration Svcs"}
]

def load_patterns(test_mode=False):
    collection_name = "patterns_test" if test_mode else "patterns"
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    patterns_col = db[collection_name]
    if patterns_col.count_documents({}) == 0:
        patterns_col.insert_many(PATTERNS)
        print(f"✅ Inserted {len(PATTERNS)} patterns into MongoDB collection '{collection_name}'.")
    else:
        print(f"ℹ️ Patterns collection '{collection_name}' already populated. Skipping insert.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load patterns into MongoDB.")
    parser.add_argument("--test", action="store_true", help="Use the _test collection")
    args = parser.parse_args()
    load_patterns(test_mode=args.test)