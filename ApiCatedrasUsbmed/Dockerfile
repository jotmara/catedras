FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY ["ApiCatedrasUsbmed.csproj", "./"]
RUN dotnet restore "ApiCatedrasUsbmed.csproj"

COPY . .
RUN dotnet build "ApiCatedrasUsbmed.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "ApiCatedrasUsbmed.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .

ENV ASPNETCORE_URLS=http://+:7045
EXPOSE 7045

ENTRYPOINT ["dotnet", "ApiCatedrasUsbmed.dll"]
