
# --------------------------- Typography Map Global Lookup
weight_map = {
    "normal": 400, "regular": 400, "bold": 700, "thin": 100, "hairline": 100,
    "extra light": 200, "ultra light": 200, "light": 300, "medium": 500,
    "semi bold": 600, "semibold": 600, "demi bold": 600, "demibold": 600,
    "extra bold": 800, "ultra bold": 800, "black": 900, "heavy": 900, 
}


# --------------------------- Helper Functions (Math and Parsing)
def get_rgb_decimals(color_string):
    #Converts 'rgb(x,y,z)' or 'rgba(x,y,z,a)' string into normalized floats (0.0 to 1.0)
    clean = color_string.replace("rgba(", "").replace("rgb(", "").replace(")", "")
    parts = clean.split(",")
    r = int(parts[0].strip()) / 255.0
    g = int(parts[1].strip()) / 255.0
    b = int(parts[2].strip()) / 255.0
    return (r, g, b)

def get_alpha(color_string):
    #Extracts the alpha value from a color string. Returns 0.0 if transparent.
    if not color_string or color_string.strip() in ("transparent", "rgba(0,0,0,0)", "rgba(0, 0, 0, 0)"):
        return 0.0
    clean = color_string.replace("rgba(", "").replace("rgb(", "").replace(")", "")
    parts = clean.split(",")
    if len(parts) == 4:
        return float(parts[3].strip())
    return 1.0 # string only has 3 part

def calculate_contrast(fg_str, bg_str):
    #Calculates official WCAG relative luminance contrast ratio
    fg_rgb = get_rgb_decimals(fg_str)
    bg_rgb = get_rgb_decimals(bg_str)
    
    luminances = []
    for rgb in (fg_rgb, bg_rgb):
        lum_channels = []
        for channel in rgb:
            if channel <= 0.03928:
                lum_channels.append(channel / 12.92)
            else:
                lum_channels.append(((channel + 0.055) / 1.055) ** 2.4)
        l = 0.2126 * lum_channels[0] + 0.7152 * lum_channels[1] + 0.0722 * lum_channels[2]
        luminances.append(l)
        
    l1, l2 = luminances[0], luminances[1]
    if l1 > l2:
        return (l1 + 0.05) / (l2 + 0.05)
    else:
        return (l2 + 0.05) / (l1 + 0.05)
