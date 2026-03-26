// Authentication service for Everbloom Archive
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user';
  created_at: string;
  last_login?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

class AuthService {
  private token: string | null = null;
  private user: User | null = null;

  constructor() {
    // Load token from localStorage on init
    this.token = localStorage.getItem('authToken');
    const userStr = localStorage.getItem('authUser');
    if (userStr) {
      this.user = JSON.parse(userStr);
    }
  }

  getToken(): string | null {
    return this.token;
  }

  getUser(): User | null {
    return this.user;
  }

  isAuthenticated(): boolean {
    return !!this.token && !!this.user;
  }

  isAdmin(): boolean {
    return this.user?.role === 'admin';
  }

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Login failed');
    }

    const data: LoginResponse = await response.json();
    
    // Store token and user
    this.token = data.access_token;
    this.user = data.user;
    
    localStorage.setItem('authToken', this.token);
    localStorage.setItem('authUser', JSON.stringify(this.user));
    
    return data;
  }

  async register(userData: RegisterData): Promise<{ user: User; message: string }> {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Registration failed');
    }

    return response.json();
  }

  async getCurrentUser(): Promise<User> {
    if (!this.token) {
      throw new Error('No authentication token');
    }

    const response = await fetch('/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get current user');
    }

    const user: User = await response.json();
    this.user = user;
    localStorage.setItem('authUser', JSON.stringify(user));
    
    return user;
  }

  logout(): void {
    this.token = null;
    this.user = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('authUser');
  }

  // Get auth headers for API requests
  getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Make authenticated API requests
  async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const headers = {
      ...this.getAuthHeaders(),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle token expiration
    if (response.status === 401) {
      this.logout();
      window.location.href = '/login';
      throw new Error('Session expired');
    }

    return response;
  }
}

// Singleton instance
export const authService = new AuthService();

// React hook for authentication
export const useAuth = () => {
  const login = authService.login.bind(authService);
  const register = authService.register.bind(authService);
  const logout = authService.logout.bind(authService);
  const getCurrentUser = authService.getCurrentUser.bind(authService);
  const authenticatedFetch = authService.authenticatedFetch.bind(authService);

  return {
    token: authService.getToken(),
    user: authService.getUser(),
    isAuthenticated: authService.isAuthenticated(),
    isAdmin: authService.isAdmin(),
    login,
    register,
    logout,
    getCurrentUser,
    authenticatedFetch,
    getAuthHeaders: authService.getAuthHeaders.bind(authService),
  };
};
