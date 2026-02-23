import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { companiesAPI } from '../services/api';

// Default theme colors - AusSuperSource branding
const defaultTheme = {
  primaryColor: '#1A56DB',  // AusSuperSource blue
  secondaryColor: '#1E40AF',
  tertiaryColor: '#0891B2',  // cyan accent
  logoUrl: '/assets/aussupersource-logo.png',
  companyName: 'AusSuperSource',
  sidebarBgColor: '#0B1A3B',  // deep navy
  sidebarTextColor: '#ffffff',
  sidebarHoverBgColor: '#1E3A6E',
};

// Convert hex to HSL for CSS variable usage
function hexToHSL(hex) {
  // Remove # if present
  hex = hex.replace('#', '');

  // Parse hex values
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;

  if (max === min) {
    h = s = 0;
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
      default: h = 0;
    }
  }

  return {
    h: Math.round(h * 360),
    s: Math.round(s * 100),
    l: Math.round(l * 100),
  };
}

// Generate color shades from a base color
function generateColorShades(hex) {
  const hsl = hexToHSL(hex);
  return {
    50: `${hsl.h} ${hsl.s}% 97%`,
    100: `${hsl.h} ${hsl.s}% 94%`,
    200: `${hsl.h} ${hsl.s}% 86%`,
    300: `${hsl.h} ${hsl.s}% 74%`,
    400: `${hsl.h} ${hsl.s}% 62%`,
    500: `${hsl.h} ${hsl.s}% 50%`,
    600: `${hsl.h} ${hsl.s}% 42%`,
    700: `${hsl.h} ${hsl.s}% 34%`,
    800: `${hsl.h} ${hsl.s}% 26%`,
    900: `${hsl.h} ${hsl.s}% 18%`,
    950: `${hsl.h} ${hsl.s}% 10%`,
  };
}

const useThemeStore = create(
  persist(
    (set, get) => ({
      // Theme state
      ...defaultTheme,
      isLoading: false,
      isLoaded: false,

      // Actions
      setTheme: (theme) => {
        set({
          primaryColor: theme.primary_color || defaultTheme.primaryColor,
          secondaryColor: theme.secondary_color || defaultTheme.secondaryColor,
          tertiaryColor: theme.tertiary_color || defaultTheme.tertiaryColor,
          logoUrl: theme.logo_url || null,
          companyName: theme.name || theme.trading_name || defaultTheme.companyName,
          sidebarBgColor: theme.sidebar_bg_color || defaultTheme.sidebarBgColor,
          sidebarTextColor: theme.sidebar_text_color || defaultTheme.sidebarTextColor,
          sidebarHoverBgColor: theme.sidebar_hover_bg_color || defaultTheme.sidebarHoverBgColor,
        });
        // Apply CSS variables
        get().applyTheme();
      },

      fetchTheme: async () => {
        try {
          set({ isLoading: true });
          const response = await companiesAPI.getMyCompany();
          const company = response.data.company;

          if (company) {
            set({
              primaryColor: company.primary_color || defaultTheme.primaryColor,
              secondaryColor: company.secondary_color || defaultTheme.secondaryColor,
              tertiaryColor: company.tertiary_color || defaultTheme.tertiaryColor,
              logoUrl: company.logo_url || defaultTheme.logoUrl,
              companyName: company.trading_name || company.name || defaultTheme.companyName,
              sidebarBgColor: company.sidebar_bg_color || defaultTheme.sidebarBgColor,
              sidebarTextColor: company.sidebar_text_color || defaultTheme.sidebarTextColor,
              sidebarHoverBgColor: company.sidebar_hover_bg_color || defaultTheme.sidebarHoverBgColor,
              isLoaded: true,
            });
            // Apply CSS variables
            get().applyTheme();
          }
        } catch (error) {
          console.error('Failed to fetch theme:', error);
          // Use defaults on error
          set({ isLoaded: true });
          get().applyTheme();
        } finally {
          set({ isLoading: false });
        }
      },

      applyTheme: () => {
        const { primaryColor, secondaryColor, tertiaryColor, sidebarBgColor, sidebarTextColor, sidebarHoverBgColor } = get();
        const root = document.documentElement;

        // Generate and apply primary color shades
        const primaryShades = generateColorShades(primaryColor);
        Object.entries(primaryShades).forEach(([shade, value]) => {
          root.style.setProperty(`--color-primary-${shade}`, value);
        });

        // Generate and apply secondary color shades
        const secondaryShades = generateColorShades(secondaryColor);
        Object.entries(secondaryShades).forEach(([shade, value]) => {
          root.style.setProperty(`--color-secondary-${shade}`, value);
        });

        // Generate and apply tertiary color shades
        const tertiaryShades = generateColorShades(tertiaryColor);
        Object.entries(tertiaryShades).forEach(([shade, value]) => {
          root.style.setProperty(`--color-tertiary-${shade}`, value);
        });

        // Also set the raw hex values for components that need them
        root.style.setProperty('--primary-color', primaryColor);
        root.style.setProperty('--secondary-color', secondaryColor);
        root.style.setProperty('--tertiary-color', tertiaryColor);

        // Set sidebar colors as CSS variables
        root.style.setProperty('--sidebar-bg-color', sidebarBgColor);
        root.style.setProperty('--sidebar-text-color', sidebarTextColor);
        root.style.setProperty('--sidebar-hover-bg-color', sidebarHoverBgColor);
      },

      resetTheme: () => {
        set({ ...defaultTheme, isLoaded: false });
        get().applyTheme();
      },
    }),
    {
      name: 'crm-theme-v2',
      partialize: (state) => ({
        primaryColor: state.primaryColor,
        secondaryColor: state.secondaryColor,
        tertiaryColor: state.tertiaryColor,
        logoUrl: state.logoUrl,
        companyName: state.companyName,
        sidebarBgColor: state.sidebarBgColor,
        sidebarTextColor: state.sidebarTextColor,
        sidebarHoverBgColor: state.sidebarHoverBgColor,
      }),
    }
  )
);

export default useThemeStore;
