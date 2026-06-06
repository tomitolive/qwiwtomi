export const TMDB_API_KEY = "882e741f7283dc9ba1654d4692ec30f6";
export const BASE_URL = "https://api.themoviedb.org/3";
export const IMAGE_BASE_URL = "/t/p/w500";

export async function getTMDBData(endpoint: string, params: Record<string, string> = {}) {
  const url = new URL(`${BASE_URL}/${endpoint}`);
  url.searchParams.append("api_key", TMDB_API_KEY);
  for (const [key, value] of Object.entries(params)) {
    url.searchParams.append(key, value);
  }

  const res = await fetch(url.toString(), { next: { revalidate: 3600 } });
  if (!res.ok) return null;
  return res.json();
}

export async function getDetails(id: string, type: "movie" | "tv") {
  const [ar, en, credits, similar, videos] = await Promise.all([
    getTMDBData(`${type}/${id}`, { language: "ar" }),
    getTMDBData(`${type}/${id}`, { language: "en" }),
    getTMDBData(`${type}/${id}/credits`),
    getTMDBData(`${type}/${id}/similar`, { language: "en-US" }),
    getTMDBData(`${type}/${id}/videos`),
  ]);
  return { ar, en, credits, similar, videos };
}
