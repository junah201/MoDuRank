import { useCustomQuery } from "./useCustomQuery";

import { getMe } from "@/api/user";
import { QUERY } from "@/constants/query";

export const useUser = () => {
  const { data, isError, isLoading } = useCustomQuery(
    [QUERY.MY_PROFILE],
    () => getMe(),
    {
      staleTime: Infinity,
      cacheTime: Infinity,
      onError: () => {},
    }
  );

  const user = isError || isLoading ? null : data?.data || null;

  return { user, isError, isLoading };
};

export default useUser;
