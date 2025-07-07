# DarziFlow App (Flutter Frontend)

This is the Flutter frontend application for DarziFlow, a tailor shop management system.

## Project Overview

This mobile application provides tailors with an interface to manage customers, orders, measurements, payments, and inventory, interacting with the DarziFlow Backend API.

## Features Implemented

The backend currently supports the following core modules, and the frontend is actively being developed:

*   **Authentication:**
    *   Backend: Secure user registration and JWT-based token authentication.
    *   Frontend: Login Screen, Logout functionality, auth state management (Riverpod), secure token storage, and auth-based navigation.
*   **Dashboard Screen:**
    *   Frontend: Displays key metrics like active orders, order counts by status, and sales summaries by fetching and processing data from the backend. Handles loading and error states.
*   **Customer Management:**
    *   Backend: Full CRUD for customers and measurements.
    *   Frontend:
        *   Customer List Screen with search, pagination, and pull-to-refresh.
        *   Add/Edit Customer Screen with form validation.
        *   Customer Detail Screen displaying customer information and their measurement sets.
        *   Dialog for Adding/Editing/Viewing measurements.
*   **Order Management:**
    *   Backend: Comprehensive order processing including items, pricing, status, assignments, and file uploads (voice notes, design images).
    *   Frontend:
        *   Order List Screen with search, status filtering, pagination, and pull-to-refresh.
        *   Create/Edit Order Screen with complex form for order details, dynamic item management, customer/karigar selection, file uploads, and pricing.
        *   Order Detail Screen displaying comprehensive order information, items, attachments, payments, and allowing status changes and payment recording.
*   **Payment Management:**
    *   Backend: Recording and managing multiple payments against orders.
    *   Frontend: Integrated into Order Detail screen (list payments, add new payment via dialog, delete payment).
*   **Retail/POS (Basic):**
    *   Frontend: A simple interface for quick retail sales of existing inventory items (accessories). Allows item selection, cart management, optional customer association, and processing the sale by creating a simplified, fully paid order.
*   **Karigar (Craftsman) Management:**
    *   Backend: Full CRUD for karigars.
    *   Frontend: (Development In Progress - basic model, service, and providers exist)
*   **Inventory Management (Basic):**
    *   Backend: Full CRUD for fabrics and accessories.
    *   Frontend: (Development In Progress - basic models, service, and providers exist; Accessories used by POS)


## Technology Stack

*   **Framework:** Flutter
*   **Programming Language:** Dart
*   **State Management:** Riverpod (`flutter_riverpod`, `hooks_riverpod`)
*   **Navigation:** GoRouter (`go_router`)
*   **HTTP Client:** `http` package
*   **Secure Storage:** `flutter_secure_storage` (for auth tokens)
*   **Simple Key-Value Storage:** `shared_preferences`
*   **Filtering:** `django-filter` (backend), client-side logic, and `flutter_riverpod` for UI state.
*   **File Picking:** `image_picker`, `file_picker`
*   **Utility:** `intl` (for formatting), `uuid` (for temporary client-side IDs)

## Project Structure

The project follows a feature-first approach for scalability:

```
darziflow_app/
├── lib/
│   ├── main.dart             # Main application entry point
│   └── src/
│       ├── app.dart            # Root application widget (MaterialApp.router)
│       ├── core/               # Core utilities, constants, themes, enums
│       ├── config/             # App configuration (e.g., API base URL)
│       ├── data/               # Data layer: models, data providers, repositories
│       ├── features/           # Feature modules (auth, dashboard, customers, orders, retail_pos etc.)
│       │   └── auth/
│       │   │   ├── screens/    # UI screens for the feature
│       │   │   ├── widgets/    # Widgets specific to this feature
│       │   │   └── providers/  # State management (Riverpod providers) for this feature
│       │   └── dashboard/
│       │   │   ├── screens/
│       │   │   └── providers/
│       │   └── customers/
│       │   │   ├── screens/
│       │   │   └── providers/
│       │   └── orders/
│       │   │   ├── screens/
│       │   │   └── providers/
│       │   └── retail_pos/
│       │       ├── screens/
│       │       └── providers/
│       │   └── ... (other features)
│       ├── navigation/         # Navigation logic, AppRoutes, GoRouter configuration
│       ├── services/           # API service classes (AuthService, CustomerService, etc.)
│       ├── shared_widgets/     # Globally reusable UI components
│       └── state_management/   # Global Riverpod providers setup (app_providers.dart)
├── assets/                 # Static assets (images, fonts, icons)
│   ├── images/
│   ├── fonts/
│   └── icons/
├── test/                   # Unit and widget tests
├── pubspec.yaml            # Dependencies and project metadata
└── README.md               # This file
```

## Getting Started (macOS Setup Guide)

Follow these instructions to set up and run the project locally on a macOS machine.

### 1. Prerequisites

*   **Flutter SDK:** Ensure you have Flutter installed (latest stable version recommended). If not, follow the official Flutter installation guide: [https://docs.flutter.dev/get-started/install/macos](https://docs.flutter.dev/get-started/install/macos)
*   **Xcode:** For building and running iOS apps. Install from the Mac App Store. After installing, open Xcode once to accept license agreements and install command-line tools if prompted: `sudo xcodebuild -license accept` and `xcode-select --install`.
*   **Android Studio:** For building and running Android apps, and for Android SDK/emulator management. Download from [https://developer.android.com/studio](https://developer.android.com/studio).
*   **Git:** For cloning the repository.
*   **An IDE:** Android Studio (with Flutter plugin), VS Code (with Flutter extension), or IntelliJ IDEA (with Flutter plugin).

### 2. Clone the Repository

```bash
git clone <your-repository-url> darziflow_app
cd darziflow_app
```
(Replace `<your-repository-url>` with the actual URL of your Git repository)

### 3. Configure Flutter

Ensure your Flutter environment is set up correctly:
```bash
flutter doctor
```
Address any issues reported by `flutter doctor`. This might involve installing Android SDK command-line tools, CocoaPods (for iOS), etc.

### 4. Install Dependencies

Fetch the Flutter packages defined in `pubspec.yaml`:
```bash
flutter pub get
```

### 5. Backend Server

Ensure the DarziFlow Backend server is running and accessible.
*   Refer to the backend's `README.md` for its setup instructions.
*   The API base URL for the Flutter app is configured in `lib/src/config/app_config.dart`.
    *   For Android Emulator connecting to a backend on the same machine: `http://10.0.2.2:8000/api/v1` (default in `app_config.dart`).
    *   For iOS Simulator or physical devices on the same Wi-Fi network: Use your computer's local network IP address (e.g., `http://192.168.1.100:8000/api/v1`). You can find your IP using `ifconfig` (macOS/Linux) or `ipconfig` (Windows) in the terminal.

### 6. Running the Application

*   **Open an Emulator/Simulator:**
    *   For Android: Open Android Studio > Virtual Device Manager (or Tools > AVD Manager) > Start an emulator.
    *   For iOS: Open Simulator (`open -a Simulator` in terminal, or via Xcode).
*   **Or, Connect a Physical Device:** Ensure developer mode and USB debugging (Android) or build to device (iOS) are set up.

*   **Run the app from your IDE or terminal:**
    ```bash
    flutter run
    ```
    To run on a specific device if multiple are connected (use `flutter devices` to list them):
    ```bash
    flutter run -d <deviceId>
    ```

### Key Libraries Used:

*   **State Management:** `flutter_riverpod` & `hooks_riverpod`
*   **Navigation:** `go_router`
*   **HTTP Client:** `http`
*   **Secure Storage:** `flutter_secure_storage`
*   **Simple Key-Value Storage:** `shared_preferences`
*   **Filtering (Backend):** `django-filter` (Backend uses this for query parameter-based filtering)
*   **File Picking:** `image_picker`, `file_picker`
*   **Utility:** `intl`, `uuid`

### API Service Layer

*   Located in `lib/src/services/`.
*   `api_service.dart` provides a base client for HTTP requests.
*   Feature-specific services (`AuthService`, `CustomerService`, `OrderService`, `InventoryService`, `KarigarService`) use `ApiService`.

### State Management (Riverpod)

*   Global service providers in `lib/src/state_management/app_providers.dart`.
*   Feature-specific state managed by `StateNotifier` classes and providers (e.g., `AuthNotifier`, `DashboardNotifier`, `CustomerListNotifier`, `OrderDetailNotifier`, `OrderFormNotifier`, `POSNotifier`).
*   App root wrapped in `ProviderScope`.

### Navigation (GoRouter)

*   Configured in `lib/src/navigation/app_router.dart`.
*   Uses `GoRouter` for declarative, URL-based routing with auth-based redirection.
*   Supports nested routes (e.g., customer measurements, order payments).

---
This README will be updated as more features and screens are developed.
```
