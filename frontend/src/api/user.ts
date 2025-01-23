import API_ROUTE from "@/constants/api";
import { ACCESS_TOEKN } from "@/constants/cookie";
import { Axios } from "@/lib/Axios";
import { UserPublic } from "@/types";

const { VITE_API_URL } = import.meta.env;

const authAxios = new Axios(true, VITE_API_URL, ACCESS_TOEKN);

export const getMe = async () => {
  const res = await authAxios.get<UserPublic>(API_ROUTE.USER.ME);

  return res;
};
