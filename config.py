import structlog


def configure_structlog():

    # Configure structlog to use Colorender processor with custom color map
    structlog.configure(
        # processors=[
        #     structlog.processors.TimeStamper(fmt="iso"),
        #     # structlog.processors.JSONRenderer(),
        #     # structlog.processors.ExceptionPrettyPrinter(),
        #     # structlog.processors.LevelFormatter(
        #     #     level_styles=COLORS,
        #     #     fmt="%(level)s: %(message)s"
        #     # ),
        #     # structlog.processors.Colourise(colors=COLORS),
        # ],
        # logger_factory=structlog.PrintLoggerFactory(),
    )
