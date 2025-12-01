# TarımPazarı - Agricultural E-Commerce Marketplace

## Overview

TarımPazarı is a comprehensive e-commerce marketplace platform that connects farmers (buyers) and agricultural suppliers (sellers). The platform facilitates the buying and selling of agricultural products, equipment, and supplies with a focus on efficient logistics and user-friendly experiences.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Technology Stack
- **Backend Framework**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM for data persistence
- **Frontend**: Server-side rendered HTML templates using Jinja2
- **UI Framework**: Bootstrap 5 (via CDN) for responsive design
- **Icons**: FontAwesome (via CDN)
- **JavaScript**: Vanilla JavaScript for dynamic interactions

### Application Architecture

**Multi-Role System**
The application implements a role-based access control system with three distinct user types:
- **Admin**: Manages seller approvals and categories
- **Seller (Supplier)**: Lists products with inventory and logistics data
- **Buyer (Farmer)**: Browses, purchases, and reviews products

**Session-Based Authentication**
User authentication is handled through Flask sessions with password hashing using Werkzeug's security utilities. User credentials are stored securely with hashed passwords in the database.

### Data Model

**Core Entities**:
- **User**: Stores user credentials, role, seller approval status, and company information
- **Category**: Organizes products into agricultural categories with icon support
- **Product**: Contains product details including price, stock, and critical logistics data (desi/volumetric weight)
- **Order**: Tracks customer orders with status, pricing, and shipping method
- **OrderItem**: Junction table linking orders to products with quantity and pricing snapshots
- **Review**: User-generated product reviews with star ratings
- **CartItem**: Session-based shopping cart for buyers

**Key Relationships**:
- One-to-many: User → Products (sellers to their listings)
- One-to-many: User → Orders (buyers to their purchases)
- One-to-many: Category → Products
- Many-to-many: Orders ↔ Products (through OrderItem)

### Hybrid Logistics Algorithm

**Problem**: Determining appropriate shipping methods based on order size and weight.

**Solution**: A threshold-based algorithm calculates total "Desi" (volumetric weight) for cart items:
- If total Desi < 30: Use "Kargo Entegrasyonu" (standard courier)
- If total Desi ≥ 30: Use "Ambar/Nakliye" (warehouse/freight shipping)

**Rationale**: Optimizes shipping costs and delivery methods based on package size. Small orders go through standard shipping, while bulk orders use freight services.

### Frontend Architecture

**Template Structure**:
- Base template with navigation, search, and cart functionality
- Page-specific templates extending the base
- Separate template directories for admin and seller panels

**Styling Approach**:
- Bootstrap 5 for responsive grid and components
- Custom CSS overrides for brand-specific design (agricultural green and orange theme)
- Trendyol/Hepsiburada-inspired UI patterns for familiarity

**Dynamic Features**:
- AJAX-based cart operations (add, update, remove items)
- Real-time cart badge updates
- Client-side form validation
- Interactive quantity selectors

### Route Architecture

**Public Routes**: Product browsing, search, filtering, product details
**Authenticated Routes**: Cart, checkout, order history, reviews
**Seller Routes**: Product management (CRUD), order fulfillment, dashboard
**Admin Routes**: User approval, category management, system overview

## External Dependencies

### CDN Resources
- **Bootstrap 5**: UI framework for responsive layouts and components
- **FontAwesome 6**: Icon library for visual elements throughout the application

### Python Packages
- **Flask**: Web application framework
- **Flask-SQLAlchemy**: ORM for database operations
- **Werkzeug**: Password hashing and security utilities (bundled with Flask)

### Database
- **SQLite**: File-based relational database (`tarim_pazari.db`)
- No external database server required
- Database initialization handled through SQLAlchemy models

### Session Management
- Flask's built-in session management using secret key
- Server-side session storage
- Session secret configurable via environment variable `SESSION_SECRET`

### Development Considerations
- Application uses environment variables for configuration (SESSION_SECRET)
- Database seeding script (`seed_data.py`) provides initial data for development
- Demo accounts available for testing all user roles