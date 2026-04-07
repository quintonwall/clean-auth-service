/**
 * Grumpy Weather API Client
 *
 * A typed client wrapping the WeatherAPI.com service with a distinctly
 * unimpressed attitude. Provides current conditions, forecasts, location
 * search, and a curated set of grumpy weather messages.
 *
 * Auth: API key passed as `key` query parameter.
 *
 * Environment variables:
 *   WEATHER_API_BASE_URL  — WeatherAPI.com base URL (e.g. https://api.weatherapi.com/v1)
 *   WEATHER_API_KEY       — Your WeatherAPI.com API key
 *   WEATHER_MOCK_BASE_URL — Mock server base URL for grumpy messages
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface WeatherCondition {
  text: string;
  icon: string;
  code: number;
}

export interface Location {
  name: string;
  region: string;
  country: string;
  lat: number;
  lon: number;
  tz_id: string;
  localtime_epoch: number;
  localtime: string;
}

export interface CurrentWeather {
  last_updated_epoch: number;
  last_updated: string;
  temp_c: number;
  temp_f: number;
  is_day: 0 | 1;
  condition: WeatherCondition;
  wind_mph: number;
  wind_kph: number;
  wind_degree: number;
  wind_dir: string;
  pressure_mb: number;
  pressure_in: number;
  precip_mm: number;
  precip_in: number;
  humidity: number;
  cloud: number;
  feelslike_c: number;
  feelslike_f: number;
  vis_km: number;
  vis_miles: number;
  uv: number;
  gust_mph: number;
  gust_kph: number;
}

export interface CurrentWeatherResponse {
  location: Location;
  current: CurrentWeather;
}

export interface ForecastDayDetail {
  maxtemp_c: number;
  maxtemp_f: number;
  mintemp_c: number;
  mintemp_f: number;
  avgtemp_c: number;
  avgtemp_f: number;
  maxwind_mph?: number;
  maxwind_kph: number;
  totalprecip_mm: number;
  totalprecip_in?: number;
  avgvis_km?: number;
  avghumidity: number;
  daily_will_it_rain?: 0 | 1;
  daily_chance_of_rain: number;
  daily_will_it_snow?: 0 | 1;
  daily_chance_of_snow: number;
  condition: WeatherCondition;
  uv: number;
}

export interface ForecastAstro {
  sunrise: string;
  sunset: string;
}

export interface ForecastDay {
  date: string;
  date_epoch?: number;
  day: ForecastDayDetail;
  astro: ForecastAstro;
}

export interface ForecastResponse {
  location: Location;
  current: Partial<CurrentWeather>;
  forecast: {
    forecastday: ForecastDay[];
  };
}

export interface SearchLocation {
  id: number;
  name: string;
  region: string;
  country: string;
  lat: number;
  lon: number;
  url: string;
}

export interface GrumpyMessages {
  sunny: string[];
  cloudy: string[];
  rainy: string[];
  snowy: string[];
  stormy: string[];
  [condition: string]: string[];
}

export interface WeatherApiError {
  error: {
    code: number;
    message: string;
  };
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export class GrumpyWeatherApiError extends Error {
  constructor(
    public readonly statusCode: number,
    public readonly code: number,
    message: string,
  ) {
    super(message);
    this.name = 'GrumpyWeatherApiError';
  }
}

export interface GrumpyWeatherClientOptions {
  /** WeatherAPI.com base URL. Defaults to WEATHER_API_BASE_URL env var. */
  baseUrl?: string;
  /** WeatherAPI.com API key. Defaults to WEATHER_API_KEY env var. */
  apiKey?: string;
  /** Mock server base URL for grumpy messages. Defaults to WEATHER_MOCK_BASE_URL env var. */
  mockBaseUrl?: string;
}

export class GrumpyWeatherApiClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly mockBaseUrl: string;

  constructor(options: GrumpyWeatherClientOptions = {}) {
    this.baseUrl =
      options.baseUrl ??
      process.env.WEATHER_API_BASE_URL ??
      'https://api.weatherapi.com/v1';
    this.apiKey = options.apiKey ?? process.env.WEATHER_API_KEY ?? '';
    this.mockBaseUrl =
      options.mockBaseUrl ?? process.env.WEATHER_MOCK_BASE_URL ?? '';

    if (!this.apiKey) {
      throw new Error(
        'Grumpy Weather API: no API key provided. Set WEATHER_API_KEY or pass apiKey in options.',
      );
    }
  }

  // -------------------------------------------------------------------------
  // Private helpers
  // -------------------------------------------------------------------------

  private buildUrl(
    base: string,
    path: string,
    params: Record<string, string | number | undefined>,
  ): string {
    const url = new URL(path, base);
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    }
    return url.toString();
  }

  private async request<T>(url: string): Promise<T> {
    const response = await fetch(url);
    const body = await response.json() as T | WeatherApiError;

    if (!response.ok) {
      const err = body as WeatherApiError;
      throw new GrumpyWeatherApiError(
        response.status,
        err.error?.code ?? response.status,
        err.error?.message ?? response.statusText,
      );
    }

    return body as T;
  }

  // -------------------------------------------------------------------------
  // Current Weather
  // -------------------------------------------------------------------------

  /**
   * Get current weather conditions for a city by name.
   *
   * @param city   City name (e.g. "London", "New York")
   * @param options.aqi  Include air quality data ("yes" | "no", default "no")
   */
  async getCurrentWeatherByCity(
    city: string,
    options: { aqi?: 'yes' | 'no' } = {},
  ): Promise<CurrentWeatherResponse> {
    const url = this.buildUrl(this.baseUrl, '/current.json', {
      key: this.apiKey,
      q: city,
      aqi: options.aqi ?? 'no',
    });
    return this.request<CurrentWeatherResponse>(url);
  }

  /**
   * Get current weather conditions by geographic coordinates.
   *
   * @param lat  Latitude
   * @param lon  Longitude
   * @param options.aqi  Include air quality data ("yes" | "no", default "no")
   */
  async getCurrentWeatherByCoordinates(
    lat: number,
    lon: number,
    options: { aqi?: 'yes' | 'no' } = {},
  ): Promise<CurrentWeatherResponse> {
    const url = this.buildUrl(this.baseUrl, '/current.json', {
      key: this.apiKey,
      q: `${lat},${lon}`,
      aqi: options.aqi ?? 'no',
    });
    return this.request<CurrentWeatherResponse>(url);
  }

  // -------------------------------------------------------------------------
  // Forecast
  // -------------------------------------------------------------------------

  /**
   * Get a weather forecast for a city by name.
   *
   * @param city   City name (e.g. "London")
   * @param days   Number of forecast days (1–10, default 3)
   * @param options.aqi     Include air quality data ("yes" | "no", default "no")
   * @param options.alerts  Include weather alerts ("yes" | "no", default "no")
   */
  async getForecastByCity(
    city: string,
    days: number = 3,
    options: { aqi?: 'yes' | 'no'; alerts?: 'yes' | 'no' } = {},
  ): Promise<ForecastResponse> {
    const url = this.buildUrl(this.baseUrl, '/forecast.json', {
      key: this.apiKey,
      q: city,
      days,
      aqi: options.aqi ?? 'no',
      alerts: options.alerts ?? 'no',
    });
    return this.request<ForecastResponse>(url);
  }

  /**
   * Get a weather forecast by geographic coordinates.
   *
   * @param lat    Latitude
   * @param lon    Longitude
   * @param days   Number of forecast days (1–10, default 3)
   * @param options.aqi     Include air quality data ("yes" | "no", default "no")
   * @param options.alerts  Include weather alerts ("yes" | "no", default "no")
   */
  async getForecastByCoordinates(
    lat: number,
    lon: number,
    days: number = 3,
    options: { aqi?: 'yes' | 'no'; alerts?: 'yes' | 'no' } = {},
  ): Promise<ForecastResponse> {
    const url = this.buildUrl(this.baseUrl, '/forecast.json', {
      key: this.apiKey,
      q: `${lat},${lon}`,
      days,
      aqi: options.aqi ?? 'no',
      alerts: options.alerts ?? 'no',
    });
    return this.request<ForecastResponse>(url);
  }

  // -------------------------------------------------------------------------
  // Search / Autocomplete
  // -------------------------------------------------------------------------

  /**
   * Search for locations matching a query string. Useful for autocomplete.
   *
   * @param query  Partial city name or coordinates string (e.g. "Lon", "Paris")
   */
  async searchLocations(query: string): Promise<SearchLocation[]> {
    const url = this.buildUrl(this.baseUrl, '/search.json', {
      key: this.apiKey,
      q: query,
    });
    return this.request<SearchLocation[]>(url);
  }

  // -------------------------------------------------------------------------
  // Grumpy Message Reference (Mock)
  // -------------------------------------------------------------------------

  /**
   * Retrieve the full catalogue of grumpy weather messages from the mock server.
   * Messages are keyed by weather condition (e.g. "sunny", "rainy", "snowy").
   */
  async getGrumpyMessages(): Promise<GrumpyMessages> {
    if (!this.mockBaseUrl) {
      throw new Error(
        'Grumpy Weather API: no mock base URL configured. Set WEATHER_MOCK_BASE_URL or pass mockBaseUrl in options.',
      );
    }
    const url = `${this.mockBaseUrl}/grumpy/messages`;
    return this.request<GrumpyMessages>(url);
  }
}
