const AUTH = {
  LOGIN: "/login",
} as const;

const USER = {
  ME: "/users/me",
  GET_BY_ID: "/users/:id",
} as const;

const API_ROUTE = {
  AUTH,
  USER,
} as const;

export default API_ROUTE;
