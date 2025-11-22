import { useQuery } from '@tanstack/react-query';
import { predictionsApi } from '../api/client';
import { format } from 'date-fns';

export const usePredictions = (date: Date, useOptimized: boolean = false) => {
  const dateStr = format(date, 'yyyy-MM-dd');
  
  return useQuery({
    queryKey: ['predictions', dateStr, useOptimized],
    queryFn: () => predictionsApi.getPredictions(dateStr, useOptimized),
    enabled: !!date,
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    gcTime: 30 * 60 * 1000, // Keep cached data for 30 minutes (gcTime replaces cacheTime in v5)
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
    refetchOnMount: false, // Don't refetch on component mount if data exists
  });
};

