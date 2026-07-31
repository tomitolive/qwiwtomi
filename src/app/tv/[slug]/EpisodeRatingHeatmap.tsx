import { getTMDBData } from "@/lib/tmdb";

interface Episode {
  episode_number: number;
  vote_average: number;
}

interface SeasonData {
  season_number: number;
  episodes: Episode[];
}

interface EpisodeRatingHeatmapProps {
  seriesId: string;
}

export default async function EpisodeRatingHeatmap({ seriesId }: EpisodeRatingHeatmapProps) {
  // Fetch series details to get total seasons
  const seriesDetails = await getTMDBData(`tv/${seriesId}`);
  if (!seriesDetails || !seriesDetails.seasons) {
    return null;
  }

  // Filter out special seasons (season 0) and get regular seasons
  const regularSeasons = seriesDetails.seasons.filter(
    (s: any) => s.season_number > 0 && s.episode_count > 0
  );

  // Fetch episode details for each season
  const seasonsData: SeasonData[] = await Promise.all(
    regularSeasons.map(async (season: any) => {
      const seasonData = await getTMDBData(`tv/${seriesId}/season/${season.season_number}`);
      return {
        season_number: season.season_number,
        episodes: seasonData?.episodes || [],
      };
    })
  );

  // Find the maximum number of episodes across all seasons
  const maxEpisodes = Math.max(
    ...seasonsData.map((s) => s.episodes.length),
    0
  );

  // Helper function to determine background color based on rating
  function getRatingColor(rating: number): string {
    if (rating >= 9.7) return "bg-blue-500";
    if (rating >= 9.0) return "bg-green-800";
    if (rating >= 8.0) return "bg-green-500";
    return "bg-yellow-500";
  }

  // Helper function to determine border color for average
  function getAverageBorderColor(rating: number): string {
    if (rating >= 9.7) return "border-blue-500";
    if (rating >= 9.0) return "border-green-800";
    if (rating >= 8.0) return "border-green-500";
    return "border-yellow-500";
  }

  // Calculate average for each season (only including valid ratings > 0)
  const seasonAverages = seasonsData.map((season) => {
    const ratings = season.episodes
      .map((ep) => ep.vote_average)
      .filter((r) => r && r > 0);
    const average = ratings.length > 0 
      ? ratings.reduce((sum, r) => sum + r, 0) / ratings.length 
      : 0;
    return average.toFixed(1);
  });

  return (
    <div className="bg-transparent border border-zinc-800 mt-6 p-4 rounded-lg">
      <h3 className="text-white font-bold mb-4 text-lg">Episode Ratings</h3>
      
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Header Row - Season Numbers */}
          <div className="flex gap-1 mb-2">
            <div className="w-12 flex-shrink-0"></div> {/* Empty corner cell */}
            {seasonsData.map((season) => (
              <div
                key={`header-${season.season_number}`}
                className="w-12 flex-shrink-0 text-center text-gray-400 text-xs font-medium"
              >
                S{season.season_number}
              </div>
            ))}
          </div>

          {/* Episode Rows */}
          {Array.from({ length: maxEpisodes }).map((_, episodeIndex) => {
            const episodeNumber = episodeIndex + 1;
            return (
              <div key={`episode-${episodeNumber}`} className="flex gap-1 mb-1">
                {/* Episode Number Label */}
                <div className="w-12 flex-shrink-0 flex items-center justify-end text-gray-400 text-xs font-medium pr-2">
                  E{episodeNumber}
                </div>
                
                {/* Rating Cells for each season */}
                {seasonsData.map((season) => {
                  const episode = season.episodes[episodeIndex];
                  // Skip if episode doesn't exist or has no valid rating (0 or null)
                  if (!episode || !episode.vote_average || episode.vote_average === 0) {
                    return (
                      <div
                        key={`${season.season_number}-${episodeNumber}`}
                        className="w-12 h-8 flex-shrink-0"
                      />
                    );
                  }
                  
                  const rating = episode.vote_average.toFixed(1);
                  const colorClass = getRatingColor(episode.vote_average);
                  
                  return (
                    <div
                      key={`${season.season_number}-${episodeNumber}`}
                      className={`w-12 h-8 flex-shrink-0 ${colorClass} rounded-sm flex items-center justify-center text-white text-xs font-bold`}
                    >
                      {rating}
                    </div>
                  );
                })}
              </div>
            );
          })}

          {/* Average Row */}
          <div className="flex gap-1 mt-3 pt-2 border-t border-zinc-800">
            <div className="w-12 flex-shrink-0 flex items-center justify-end text-gray-400 text-xs font-bold pr-2">
              AVG
            </div>
            {seasonAverages.map((avg, index) => {
              const avgValue = parseFloat(avg);
              const borderColorClass = getAverageBorderColor(avgValue);
              return (
                <div
                  key={`avg-${index}`}
                  className={`w-12 h-8 flex-shrink-0 flex items-center justify-center text-white text-xs font-bold border-b-2 ${borderColorClass}`}
                >
                  {avg}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
