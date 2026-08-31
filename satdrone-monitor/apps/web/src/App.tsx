import SatelliteAltIcon from "@mui/icons-material/SatelliteAlt";
import {
  Alert,
  AppBar,
  Box,
  Chip,
  Container,
  CssBaseline,
  Grid2,
  Paper,
  Stack,
  ThemeProvider,
  Toolbar,
  Typography,
  createTheme,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { fetchSystemStatus } from "./api";
import { OperationsMap } from "./components/OperationsMap";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#2dd4bf" },
    background: { default: "#07111f", paper: "#0d1b2a" },
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", sans-serif',
  },
});

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <Paper className="metric">
      <Typography color="text.secondary" variant="overline">
        {label}
      </Typography>
      <Typography variant="h4">{value}</Typography>
    </Paper>
  );
}

export default function App() {
  const system = useQuery({
    queryKey: ["system-status"],
    queryFn: fetchSystemStatus,
    refetchInterval: 10_000,
    retry: 1,
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" color="transparent" elevation={0}>
        <Toolbar>
          <SatelliteAltIcon color="primary" sx={{ mr: 1.5 }} />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            SatDrone Monitor
          </Typography>
          <Chip
            color={system.isSuccess ? "success" : "warning"}
            label={system.isSuccess ? "Systems online" : "Connecting"}
            size="small"
          />
        </Toolbar>
      </AppBar>
      <Container maxWidth={false} sx={{ py: 2 }}>
        {system.isError && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Platform services are not reachable. Map monitoring remains available.
          </Alert>
        )}
        <Grid2 container spacing={2}>
          <Grid2 size={{ xs: 12, md: 8 }}>
            <Paper className="map-panel">
              <OperationsMap />
              <Box className="map-title">
                <Typography variant="overline">Live operations</Typography>
                <Typography variant="h5">Regional monitoring area</Typography>
              </Box>
            </Paper>
          </Grid2>
          <Grid2 size={{ xs: 12, md: 4 }}>
            <Stack spacing={2}>
              <Grid2 container spacing={2}>
                <Grid2 size={6}>
                  <Metric label="Active drones" value="0" />
                </Grid2>
                <Grid2 size={6}>
                  <Metric label="Open anomalies" value="0" />
                </Grid2>
              </Grid2>
              <Paper sx={{ p: 2 }}>
                <Typography variant="overline" color="text.secondary">
                  Service mesh
                </Typography>
                <Stack spacing={1} sx={{ mt: 1 }}>
                  {Object.entries(system.data?.services ?? {}).map(
                    ([name, status]) => (
                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        key={name}
                      >
                        <Typography sx={{ textTransform: "capitalize" }}>
                          {name}
                        </Typography>
                        <Chip
                          color={status === "operational" ? "success" : "error"}
                          label={status}
                          size="small"
                          variant="outlined"
                        />
                      </Stack>
                    ),
                  )}
                </Stack>
              </Paper>
            </Stack>
          </Grid2>
        </Grid2>
      </Container>
    </ThemeProvider>
  );
}

