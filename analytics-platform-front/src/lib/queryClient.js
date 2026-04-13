import { QueryClient } from "@tanstack/react-query";

const LONG_CACHE_MS = 24 * 60 * 60 * 1000;

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: Number.POSITIVE_INFINITY,
            gcTime: LONG_CACHE_MS,
            cacheTime: LONG_CACHE_MS,
            refetchOnMount: false,
            refetchOnWindowFocus: false,
            refetchOnReconnect: false,
            refetchInterval: false,
            retry: 0,
        },
    },
});
