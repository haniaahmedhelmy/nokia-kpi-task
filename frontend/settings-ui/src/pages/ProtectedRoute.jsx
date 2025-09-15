import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { api } from "../api";
import { CircularProgress, Box } from "@mui/material";

export default function ProtectedRoute({ children }) {
  const [ok, setOk] = useState(null);

  useEffect(() => {
    api.me().then(() => setOk(true)).catch(() => setOk(false));
  }, []);

  if (ok === null) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!ok) return <Navigate to="/login" replace />;

  return children;
}
