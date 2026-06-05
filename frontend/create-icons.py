"""
Simple script to create placeholder icons for the extension
Requires PIL/Pillow: pip install pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_shield_icon(size):
        """Create a simple shield icon"""
        # Create image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Shield outline
        shield_color = (79, 70, 229, 255)  # Primary color from CSS
        outline_color = (67, 56, 202, 255)  # Darker shade
        
        # Calculate shield dimensions
        margin = size // 8
        width = size - 2 * margin
        height = size - 2 * margin
        
        # Draw shield shape (simplified)
        points = [
            (size // 2, margin),  # Top center
            (size - margin, margin + height // 4),  # Top right
            (size - margin, margin + height * 3 // 4),  # Bottom right
            (size // 2, size - margin),  # Bottom center (point)
            (margin, margin + height * 3 // 4),  # Bottom left
            (margin, margin + height // 4),  # Top left
        ]
        
        # Draw filled shield
        draw.polygon(points, fill=shield_color, outline=outline_color)
        
        # Draw checkmark
        check_color = (255, 255, 255, 255)
        line_width = max(2, size // 16)
        
        # Checkmark coordinates
        check_start = (size // 3, size // 2)
        check_mid = (size // 2 - line_width, size * 2 // 3)
        check_end = (size * 2 // 3 + line_width, size // 3)
        
        draw.line([check_start, check_mid], fill=check_color, width=line_width)
        draw.line([check_mid, check_end], fill=check_color, width=line_width)
        
        return img
    
    # Create icons directory
    os.makedirs('icons', exist_ok=True)
    
    # Generate all required sizes
    sizes = [16, 32, 48, 128]
    
    for size in sizes:
        icon = create_shield_icon(size)
        filename = f'icons/icon{size}.png'
        icon.save(filename, 'PNG')
        print(f'✓ Created {filename}')
    
    print('\n✅ All icons created successfully!')
    print('Icons are located in the icons/ folder')
    
except ImportError:
    print('Error: PIL/Pillow not installed')
    print('Install it with: pip install pillow')
    print('\nAlternatively, create icons manually:')
    print('- Use an online icon generator (https://favicon.io/)')
    print('- Or use any image editor to create:')
    print('  - icon16.png (16x16)')
    print('  - icon32.png (32x32)')
    print('  - icon48.png (48x48)')
    print('  - icon128.png (128x128)')
    print('- Save all icons in the icons/ folder')
