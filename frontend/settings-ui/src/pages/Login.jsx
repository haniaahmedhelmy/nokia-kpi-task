import { Box, TextField, Button, Typography, Paper } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useState, useEffect } from "react";

export default function Login() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");

  const sentences = [
    "Nokia helps you realize your digital potential with networking technology that provides superior performance.",
    "Nokia Bell Labs celebrates 100 years of innovation and looks ahead to another century of discovery.",
    "Networks for enterprises and governments.",
    "Nokia is a trusted partner to the defense community and an innovation leader in cloud, fixed and wireless networks",
    "The best way to predict the future is to invent it.",
  ];

  const [sentenceIndex, setSentenceIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSentenceIndex((prev) => (prev + 1) % sentences.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    try {
      await api.login(email, pw);
      nav("/settings", { replace: true });
    } catch {
      setErr("Invalid email or password");
    }
  }

  return (
    <Box sx={{ minHeight: "100vh", position: "relative", overflow: "hidden" }}>
      <video
        autoPlay
        muted
        loop
        playsInline
        src="/NokiaVid.mp4"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          zIndex: -2,
        }}
      />

      <Box
        sx={{
          position: "absolute",
          inset: 0,
          bgcolor: "rgba(0,0,0,0.45)",
          zIndex: -1,
        }}
      />

      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          height: "100vh",
          px: { xs: 2, md: 8 },
        }}
      >
        <Box sx={{ color: "white", maxWidth: 500, minHeight: 60 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2 }}>
            Welcome Back
          </Typography>

          <Box sx={{ minHeight: 60, display: "flex", alignItems: "flex-start" }}>
            <Typography variant="body1" sx={{ opacity: 0.9 }}>
              {sentences[sentenceIndex]}
            </Typography>
          </Box>
        </Box>

        <Box
          component="form"
          onSubmit={onSubmit}
          sx={{
            display: "grid",
            gap: 2,
            width: "100%",
            maxWidth: 360,
          }}
        >
          <Paper elevation={4} sx={{ p: 1, borderRadius: 2 }}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={email}
              required
              onChange={(e) => setEmail(e.target.value)}
            />
          </Paper>

          <Paper elevation={4} sx={{ p: 1, borderRadius: 2 }}>
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={pw}
              required
              onChange={(e) => setPw(e.target.value)}
            />
          </Paper>

          {err && <Typography color="error">{err}</Typography>}

          <Button
            type="submit"
            variant="contained"
            size="large"
            sx={{
              bgcolor: "#141E61",
              color: "white",
              fontWeight: 600,
              borderRadius: 2,
              "&:hover": { bgcolor: "#0d1547" },
            }}
          >
            Sign in
          </Button>
        </Box>
      </Box>
    </Box>
  );
}
