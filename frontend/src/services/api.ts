// API Service for Everbloom Archive
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Types
export interface LifeEvent {
  id: string;
  event_year: number;
  title: string;
  description?: string;
  location_name?: string;
  coordinates?: [number, number];
  is_featured: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Gallery {
  id: string;
  event_id?: string;
  media_url: string;
  caption?: string;
  is_featured: boolean;
  media_type: string;
  title?: string;
  description?: string;
  file_size?: number;
  width?: number;
  height?: number;
  created_at: string;
}

export interface Tribute {
  id: string;
  author_name: string;
  relation_to_deceased?: string;
  message: string;
  candle_lit: boolean;
  email?: string;
  approved: boolean;
  created_at: string;
}

export interface TributePublic {
  id: string;
  author_name: string;
  relation_to_deceased?: string;
  message: string;
  candle_lit: boolean;
  created_at: string;
}

// Generic API request function
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error: ${response.status} - ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Life Events API
export const lifeEventsApi = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    featured?: boolean;
    year?: number;
  }): Promise<LifeEvent[]> => {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.featured !== undefined) searchParams.set('featured', params.featured.toString());
    if (params?.year) searchParams.set('year', params.year.toString());
    
    const query = searchParams.toString();
    return apiRequest<LifeEvent[]>(`/life-events${query ? `?${query}` : ''}`);
  },

  getById: async (id: string): Promise<LifeEvent> => {
    return apiRequest<LifeEvent>(`/life-events/${id}`);
  },

  create: async (event: Omit<LifeEvent, 'id' | 'created_at' | 'updated_at'>): Promise<LifeEvent> => {
    return apiRequest<LifeEvent>('/life-events', {
      method: 'POST',
      body: JSON.stringify(event),
    });
  },
};

// Gallery API
export const galleryApi = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    featured?: boolean;
    event_id?: string;
  }): Promise<Gallery[]> => {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.featured !== undefined) searchParams.set('featured', params.featured.toString());
    if (params?.event_id) searchParams.set('event_id', params.event_id);
    
    const query = searchParams.toString();
    return apiRequest<Gallery[]>(`/gallery${query ? `?${query}` : ''}`);
  },

  getById: async (id: string): Promise<Gallery> => {
    return apiRequest<Gallery>(`/gallery/${id}`);
  },

  create: async (formData: FormData): Promise<Gallery> => {
    const response = await fetch(`${API_BASE_URL}/gallery`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error: ${response.status} - ${errorText}`);
    }

    return await response.json();
  },
};

// Tributes API
export const tributesApi = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    approved_only?: boolean;
    candles_only?: boolean;
  }): Promise<TributePublic[]> => {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.approved_only !== undefined) searchParams.set('approved_only', params.approved_only.toString());
    if (params?.candles_only !== undefined) searchParams.set('candles_only', params.candles_only.toString());
    
    const query = searchParams.toString();
    return apiRequest<TributePublic[]>(`/tributes${query ? `?${query}` : ''}`);
  },

  create: async (tribute: Omit<Tribute, 'id' | 'approved' | 'created_at'>): Promise<Tribute> => {
    return apiRequest<Tribute>('/tributes', {
      method: 'POST',
      body: JSON.stringify(tribute),
    });
  },

  lightCandle: async (id: string): Promise<Tribute> => {
    return apiRequest<Tribute>(`/tributes/${id}/light-candle`, {
      method: 'POST',
    });
  },
};

// Health check
export const healthCheck = async (): Promise<{ status: string }> => {
  return apiRequest<{ status: string }>('/health');
};
