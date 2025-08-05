# Project & Resource Tree Structure

## Overview
The Tree Structure feature provides a hierarchical view of all projects and their assigned resources in a visually appealing, organized format. This feature helps you understand the relationship between projects and resources at a glance.

## Features

### 🌳 Hierarchical Display
- **Projects by Period**: Projects are grouped by year and month for easy navigation
- **Resource Assignment**: Clear visualization of which resources are assigned to each project
- **Project Profiles**: Highlighted display of the main profile/resource for each project

### 📊 Summary Statistics
- Total number of projects and resources
- Total billable hours across all projects
- Overall utilization percentage
- Quick overview cards with key metrics

### 🎨 Modern UI Design
- Responsive design that works on desktop and mobile
- Beautiful gradients and modern styling
- Interactive hover effects and animations
- Color-coded sections for easy identification

## How to Access

### Method 1: Navigation Menu
1. Click on the "Tree Structure" link in the main navigation bar
2. The link is located in the top navigation with a tree icon

### Method 2: Dashboard Button
1. Go to the main dashboard
2. Click the "View Tree Structure" button at the top of the page

### Method 3: Direct URL
Navigate directly to: `/tree-structure/`

## What You'll See

### Summary Cards
- **Total Projects**: Count of all active projects
- **Total Resources**: Count of all active resources
- **Billable Hours**: Total billable hours across all projects
- **Utilization Rate**: Percentage of billable vs total hours

### Project Sections
Each project displays:
- **Project Name** with type indicator
- **Key Metrics**: Present days, billable days, billable hours, non-billable days, utilization percentage
- **Project Profile**: The main resource assigned to the project
- **Assigned Resources**: All resources working on the project with their present days

### Period Organization
- Projects are grouped by year and month
- Most recent periods appear first
- Each period shows the number of projects it contains

## Technical Details

### Files Created/Modified
- `projects/views.py` - Added `tree_structure_view` function
- `projects/urls.py` - Added URL pattern for tree structure
- `projects/templates/projects/tree_structure.html` - Main template
- `projects/templatetags/project_filters.py` - Custom template filter
- `templates/base.html` - Added navigation link
- `templates/home.html` - Added quick access button

### Dependencies
- Django 5.2.4+
- Font Awesome (for icons)
- Bootstrap 5 (for styling)

## Usage Tips

1. **Quick Overview**: Use the summary cards to get a high-level view of your project portfolio
2. **Resource Allocation**: Easily see which resources are working on multiple projects
3. **Period Analysis**: Focus on specific time periods to understand project distribution
4. **Utilization Tracking**: Monitor project utilization rates to identify underutilized projects

## Future Enhancements

Potential improvements could include:
- Filtering by project type or resource
- Export functionality (PDF/Excel)
- Interactive charts and graphs
- Drill-down capabilities for detailed resource information
- Search and filter functionality

## Support

If you encounter any issues with the tree structure feature, please check:
1. All Django migrations are applied
2. Font Awesome is loading correctly
3. JavaScript is enabled in your browser
4. The template files are in the correct locations 