import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { companiesAPI } from '../services/api';

const useCompanyStore = create(
  persist(
    (set, get) => ({
      company: null,
      currencies: [],
      taxTypes: [],
      isLoading: false,
      error: null,

      // Fetch company settings (including currency/tax)
      fetchCompany: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await companiesAPI.getMyCompany();
          const companyData = response.data.company;
          set({
            company: companyData,
            isLoading: false,
          });
          return companyData;
        } catch (error) {
          set({
            isLoading: false,
            error: error.response?.data?.error || 'Failed to fetch company',
          });
          return null;
        }
      },

      // Fetch available currencies
      fetchCurrencies: async () => {
        try {
          const response = await companiesAPI.getCurrencies();
          const currencyList = response.data.data?.currencies || [];
          set({ currencies: currencyList });
          return currencyList;
        } catch (error) {
          console.error('Failed to fetch currencies:', error);
          return [];
        }
      },

      // Fetch available tax types
      fetchTaxTypes: async () => {
        try {
          const response = await companiesAPI.getTaxTypes();
          const taxTypesList = response.data.data?.tax_types || [];
          set({ taxTypes: taxTypesList });
          return taxTypesList;
        } catch (error) {
          console.error('Failed to fetch tax types:', error);
          return [];
        }
      },

      // Update company in store
      updateCompany: (companyData) => {
        set({ company: { ...get().company, ...companyData } });
      },

      // Get currency settings from company
      getCurrencySettings: () => {
        const { company } = get();
        return company?.currency_settings || {
          currency: 'AUD',
          currency_symbol: '$',
          tax_type: 'GST',
          tax_label: 'GST',
          default_tax_rate: 10.00,
        };
      },

      // Format price with company currency symbol
      formatPrice: (amount, includeSymbol = true) => {
        const { currency_symbol } = get().getCurrencySettings();
        const formattedAmount = parseFloat(amount || 0).toFixed(2);
        return includeSymbol ? `${currency_symbol}${formattedAmount}` : formattedAmount;
      },

      // Get tax label (GST, VAT, etc.)
      getTaxLabel: () => {
        const { tax_label } = get().getCurrencySettings();
        return tax_label || 'GST';
      },

      // Get default tax rate
      getTaxRate: () => {
        const { default_tax_rate } = get().getCurrencySettings();
        return parseFloat(default_tax_rate || 10);
      },

      // Calculate tax amount
      calculateTax: (amount) => {
        const taxRate = get().getTaxRate();
        return parseFloat(amount || 0) * (taxRate / 100);
      },

      // Calculate total with tax
      calculateTotalWithTax: (amount) => {
        const taxRate = get().getTaxRate();
        return parseFloat(amount || 0) * (1 + taxRate / 100);
      },

      // Clear store
      clear: () => {
        set({
          company: null,
          currencies: [],
          taxTypes: [],
          isLoading: false,
          error: null,
        });
      },
    }),
    {
      name: 'company-storage',
      partialize: (state) => ({
        company: state.company,
      }),
    }
  )
);

export default useCompanyStore;
