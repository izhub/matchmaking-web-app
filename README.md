# MyMate - Matchmaking Website

### Description:

MyMate is a Flask-based web application that allows users to create profiles and connect based on shared interests. The platform allows users to register, create detailed profiles, browse other members, like profiles, and manage account preferences. Some premium features, such as messaging, are reserved for upgraded (Gold) members.
- Video Demo:  https://youtu.be/PdKI3xSBsgs


## Setup

1. Create virtual environment and activate:

    ```bash
    python -m venv venv

    # Windows PowerShell
    venv\Scripts\Activate
    
    # Mac/Linux
    source venv/bin/activate

2. Install dependencies:
    ```bash
    pip install -r requirements.txt

3. Use the sample database:
    ```bash
    Mac/Linux:
      cp sample_matrimonial.db matrimonial.db

    Windows PowerShell:
      Copy-Item sample_matrimonial.db matrimonial.db

4. Run the app:
    
        flask run


5. Test Users:
    ```bash
    Female username: jane 
    Male username: john
    password: RM!=93vbDmkn.)k

---

## Technical Highlights

- Server-side authentication and validation
- Password hashing
- Session management
- Multi-step registration enforcement
- Toggle-based like and block system
- Role-based feature access (Basic vs Gold members)
- Search filtering with pagination
- Database data transformation (height conversion)

---

## Project Goal

The goal of this project was to design and implement a structured matchmaking platform that enforces profile completeness, offers searchable user data, supports membership tiers, and provides a scalable foundation for messaging and photo-sharing features in future development.

This project demonstrates backend validation, authentication systems, relational data handling, session control, user interaction logic, and structured UI navigation.

---

## Project Overview & Flow

When visiting the website, a user may:

- Log in (if they already have an account)
- Register for a new account

### Login Page

The login system includes:

- Username and password validation (server-side)
- Password hashing verification
- Session-based authentication (user ID stored in session)
- “Show Password” checkbox
- “Forgot Password” link for password reset

Additionally, upon login the system checks whether the user has completed all required registration sections (Profile, Partner Preference, and Contact Information). If any section is incomplete, the user is redirected to complete it before accessing the site. Only fully completed registrations can access the Index page.

---

## Registration Process (4-Part System)

The registration process is divided into four required parts:

### 1. Account Registration
- Unique username required
- Unique email required
- Password requirements:
  - Minimum 8 characters
  - Must include uppercase, lowercase, and numbers
- Password confirmation required
- Age validation (front-end and server-side) – must be at least 18 years old
- Security question and answer for password retrieval
- Must agree to Terms & Conditions (linked)

### 2. Profile Creation
- General bio-data information
- “About Me” and “Looking For” fields with show less/more toggle
- Gender-based colored profile labels
- Height stored in inches in the database and converted to feet for display
- Like button (toggle to add to favorites)
- Message button (Gold members only)
- Report button (leads to report form)
- Block toggle (with unblock option in preferences)

### 3. Partner Preference
- Criteria describing the type of partner the user is seeking

### 4. Contact Information
- Required contact-related information

Only after completing all four sections can the user access the platform.

All users are registered as Basic members by default. Messaging functionality is restricted to Gold members.

---

## Navigation

Once logged in and profile-complete, users have access to navigation links located in the upper-right corner:

- Home
- Search
- Messages
- Logout

On the upper-left corner, the website name links back to the homepage.

---

## Index Page (Dashboard)

After login, users land on the Index page, which contains:

### 1. Profile Card (Left Panel)
- My Likes (link to Likes page)
- My Profile (view own profile)
- Preferences
- View Photo Gallery (Not Implemented)

### 2. Messaging Panel
- Reserved for viewing messages (Not Implemented)

### 3. Profiles Panel (Tabbed)
Three profile tabs are available:
- All Profiles
- Local Profiles (based on region proximity)
- Latest Profiles (registered within the last 6 months)

---

## Likes Page

The Likes page includes two tabs:

1. Profiles the user has liked
2. Members who have liked the user’s profile

The Like feature is implemented as a toggle system to add or remove favorites.

---

## User Profile Page

When viewing a user’s profile:

### Left Side
- Profile card with:
  - Profile photo
  - Username
  - Age
  - Like button (toggle)
  - Message button (Gold members only)
- Report button (leads to reporting form page)
- Block toggle (can block/unblock user)

### Right Side
- General bio-data
- Partner preferences
- “Show less/more” functionality for long text
- Height conversion (inches → feet display)
- Gender-based colored profile labels

Blocked users can also be managed from the Preferences page.

---

## Search Page

The Search page allows advanced profile searching with:

- Pagination
- Adjustable number of entries shown
- General search
- Cumulative column filtering by:
  - Name
  - Gender
  - Age
  - Height
  - Profession
  - State
  - Country
  - Origin

---

## Preferences Page

The Preferences page allows full account management.

### 1. Preferences Settings
- Profile show/hide
- Messages on/off
- Photos show/hide

### 2. Edit Sections
- Edit Profile
- Edit Partner Preference
- Edit Contact Information

### 3. Photos (Not Implemented)
- Edit Photos
- Photo Access

### 4. Account & Security
- Change Username
- Change Password
- Change Email
- Membership History
- Blocked Users (with unblock capability)
- Delete Profile

---

## Additional Notes

The following features are not yet implemented:
- Messaging system (UI exists but not functional)
- Photo gallery management
- Admin panel
- Gold members upgrade

These may be considered in future development.


