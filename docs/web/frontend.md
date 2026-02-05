# Frontend & UX Design

The user interface of the Web Dashboard is built with a focus on **clarity, responsiveness, and immediate insight**. Using Streamlit's reactive component system, the frontend transforms complex JSON telemetry into an intuitive visual story.

The goal is to move beyond the "spreadsheet look" of traditional monitoring tools and create a modern, dashboard-style experience.

---

## 🎨 Design Philosophy

The design follows three core principles:

1.  **"Glanceability":** A user should be able to understand their system's health status within 5 seconds of opening the page.
2.  **Visual Hierarchy:** Critical alerts (like overheating) are displayed prominently at the top, while granular details (like specific process IDs) are tucked away in expandable sections.
3.  **Minimalism:** We reduce cognitive load by hiding configuration options in the sidebar, leaving the main stage dedicated purely to data visualization.

---

## 📊 Visual Components

The application utilizes a rich set of interactive widgets to represent different types of data:

### 1. The "Metric" Row
At the very top of the dashboard, users see high-level Delta Metrics. These show current values compared to the previous hour.
* *Example:* "CPU Temp: 45°C (↓ 2°C)" — The arrow and color (Green/Red) immediately indicate if the trend is improving or worsening.

### 2. Time-Series Charts
We use interactive line charts to display historical performance.
* **Interactivity:** Users can zoom, pan, and hover over specific data points to see exact values.
* **Correlation:** CPU load and Temperature are often plotted on the same axis, allowing users to visually confirm that a spike in usage caused a spike in heat.

### 3. Gauge Indicators
For limits that have a hard ceiling (like RAM or Battery), we use progress bars or gauge charts. This provides a clear visual representation of "how much headroom is left" before the system hits a bottleneck.

---

## 📱 Layout & Navigation

The layout is divided into two distinct zones to maintain focus:

### The Sidebar (Control Zone)
The left-hand sidebar contains all input controls. This is where the user selects:
* Which device to monitor (if they have multiple).
* The time range for the analysis (e.g., "Last 24 Hours").
* Navigation between the "Dashboard," "Chatbot," and "Settings" pages.

### The Main Stage (Data Zone)
The central area is strictly for output. It adapts based on the sidebar selections. By separating controls from data, we ensure the charts are never obscured by menus.

---

## 🌗 Theming & Responsiveness

### Dark Mode & Light Mode
The interface automatically detects the user's system preference.
* **Dark Mode:** The default for most technical users, reducing eye strain during late-night debugging sessions.
* **Light Mode:** High-contrast mode for well-lit environments.

### Mobile Adaptability
Since Streamlit designs are responsive by default, the dashboard automatically restacks components for mobile screens. A user viewing the dashboard on a smartphone sees a simplified, vertical layout, ensuring they can check their server's health while on the go without needing a separate mobile app.