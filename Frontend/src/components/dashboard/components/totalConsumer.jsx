import { Paper, Stack, Typography } from "@mui/material";


function TotalConsumer({ totalConsumer, isMobile }) {
    return (
        <Stack direction="row" justifyContent="space-between" gap={2}>
            {totalConsumer && totalConsumer.map((c) => (
                <Paper sx={{ width: "100%", height: isMobile ? 50 : 80, p: 1, border:"1px solid grey" }}>
                    <Stack direction="row">
                        <Typography variant="h6" sx={{color:c.color}}>
                            {c.label}
                        </Typography>
                    </Stack>
                    <Stack alignItems="center">
                        <Typography variant="5" justifySelf="center">
                            {c.count}
                        </Typography>
                    </Stack>
                </Paper>
            ))}
        </Stack>
    )
}
export default TotalConsumer