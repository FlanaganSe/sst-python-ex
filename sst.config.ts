/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "sst-python-ai-api",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
      providers: {
        aws: {
          region: "us-east-1",
        },
      },
    };
  },
  async run() {
    const isProduction = $app.stage === "production";

    const api = new sst.aws.Function("ApiFunction", {
      handler: "functions/src/functions/handler.handler",
      runtime: "python3.12",
      architecture: "arm64",
      timeout: isProduction ? "30 seconds" : "15 seconds",
      memory: isProduction ? "1024 MB" : "512 MB",

      url: {
        cors: {
          allowCredentials: false,
          allowHeaders: ["content-type", "authorization", "x-api-key"],
          allowMethods: ["*"],
          allowOrigins: isProduction ? ["https://yourdomain.com"] : ["*"],
          exposeHeaders: ["x-request-id"],
          maxAge: "1 day",
        },
      },

      environment: {
        STAGE: $app.stage,
        LOG_LEVEL: isProduction ? "INFO" : "DEBUG",
        POWERTOOLS_SERVICE_NAME: "api",
        POWERTOOLS_LOG_LEVEL: isProduction ? "INFO" : "DEBUG",
        BEDROCK_MODEL_ID: "amazon.nova-lite-v1:0",
        AI_TIMEOUT: "30",
      },

      logging: {
        retention: isProduction ? "1 month" : "1 week",
        format: "json",
      },

      permissions: [
        {
          actions: [
            "bedrock:Converse",
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream",
          ],
          resources: [
            "arn:aws:bedrock:*::foundation-model/amazon.nova-lite-v1:0",
            "arn:aws:bedrock:*::foundation-model/amazon.nova-pro-v1:0",
          ],
        },
        {
          actions: ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
          resources: [
            `arn:aws:logs:*:*:log-group:/aws/lambda/sst-python-ai-api-${$app.stage}-ApiFunction*`,
          ],
        },
      ],
    });

    return { apiUrl: api.url, functionName: api.name, stage: $app.stage };
  },
});
